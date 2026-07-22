# ADR 0008: Real Authentication, Shared Base Models, and Finance Webhook Hardening

## Status

Accepted

## Context

A gap analysis against the 12-module plan found that Module 1 (Authentication) had no
real implementation: `apps.identity` exposed `/me/` and `/rbac/check/` (ADR 0002) but no
way to actually sign in — no registration, login, token issuance, password reset, or
email verification. `DEFAULT_AUTHENTICATION_CLASSES` was Session + Basic auth only,
which no web/mobile client could use. ADR 0002 explicitly listed "Add JWT/OAuth
strategy" as a follow-up; this ADR closes that gap.

The same audit found two things that had to be fixed before or alongside Module 1:

1. **No shared base model / audit-log infrastructure.** Every app hand-declared its own
   `id`/`created_at`/`updated_at` fields identically, and there was no generic audit
   trail — later modules (Documents, Voting, Analytics) all need this foundation.
2. **A live security hole in Finance.** `PaymentWebhookIngestView` accepted any POSTed
   JSON as `{"provider": ..., "payload": ...}` with `AllowAny` and no signature
   verification, meaning anyone could credit a fake `LedgerEntry` to the books.

## Decision

### Shared base models (`apps.common`)

Added `apps/common/models.py`: `UUIDModel`, `TimeStampedModel` (abstract, matching the
field definitions every app already used by hand) and `SoftDeleteModel` (adds
`deleted_at` + a manager that excludes soft-deleted rows, `all_objects` for the full
table). Added a concrete `AuditLog` model and `apps/common/audit.py::record_audit_event()`
as the one reusable audit-trail entry point for all apps.

Retrofitted `Role`, `User`, `Membership`, `Event`, `EventRegistration`, `Notification`,
`LedgerEntry`, `PaymentTransaction`, `PaymentWebhookEvent`, `Product`, `ShopOrder` to
inherit the shared abstracts instead of re-declaring the same fields. **Exception:**
`Role` originally had an implicit `BigAutoField` PK (not an explicit UUID field like
every other model) — switching it to `UUIDModel` produces a `bigint`→`uuid` `ALTER
COLUMN` that Postgres cannot cast in place (confirmed by running the migration against
real Postgres, not just SQLite, which silently "succeeds" due to weak typing). `Role`
therefore keeps its original PK type; migrating it to UUID is left as a dedicated
future data migration (regenerate ids, repoint the `identity_user_roles` FK), not
something to fold into a "safe" retrofit.

Applied `SoftDeleteModel` to `shop.Product` and `events.Event` — the two cases where a
hard delete would cascade into historical `ShopOrderItem`/`EventRegistration` rows.
Added `deactivate_product()` and `cancel_event()` services plus
`POST /api/shop/products/<id>/deactivate/` and `POST /api/events/<id>/cancel/`
endpoints (both role-gated); `cancel_event` also records an audit event and notifies
registered attendees.

### Finance webhook signature verification

Replaced the single `PaymentWebhookIngestView` (which trusted any JSON body) with two
provider-specific endpoints matching each provider's real webhook shape:

- `POST /api/finance/payments/webhooks/stripe/` — verifies `Stripe-Signature` over the
  raw request body via the official `stripe` SDK's `Webhook.construct_event()` before
  any parsing or DB write.
- `POST /api/finance/payments/webhooks/paypal/` — verifies via PayPal's server-side
  `/v1/notifications/verify-webhook-signature` API (the documented approach; PayPal
  webhooks aren't locally HMAC-verifiable the way Stripe's are).

Both fail closed: an unset `STRIPE_WEBHOOK_SECRET` / `PAYPAL_WEBHOOK_ID` outside `DEBUG`
raises rather than silently skipping verification. A request that fails verification
never reaches `process_webhook()`, so no `LedgerEntry` can be created from an unverified
payload. This is a breaking API change to the previous (already-unusable) contract —
the old `{"provider": ..., "payload": ...}` wrapper never matched what Stripe/PayPal
actually send, so there was no real integration to preserve.

### Authentication (Module 1)

Added `djangorestframework-simplejwt` (with `token_blacklist` for real logout).
`DEFAULT_AUTHENTICATION_CLASSES` now leads with `JWTAuthentication`, keeping
`SessionAuthentication` for the Django admin/Unfold.

New `apps.identity` endpoints (same clean-architecture layering as ADR 0002 —
`application/*_service.py` for business rules, `presentation/views.py` for transport):

- `POST /api/identity/register/` — creates an inactive `User`, assigns the default
  `member` role, issues an `EmailVerificationToken`, and enqueues a verification email.
- `POST /api/identity/verify-email/` — activates the user on a valid, unconsumed,
  unexpired token.
- `POST /api/auth/login/`, `POST /api/auth/refresh/` — thin wrappers around simplejwt's
  views; login also returns the `CurrentUserSerializer` payload alongside the tokens.
- `POST /api/auth/logout/` — blacklists the refresh token.
- `POST /api/identity/password-reset/`, `POST /api/identity/password-reset/confirm/` —
  Django's built-in `PasswordResetTokenGenerator`; the request endpoint always returns
  202 regardless of whether the email exists, to avoid account-enumeration.
- `POST /api/identity/roles/assign/`, `POST /api/identity/roles/revoke/` — admin-only,
  now audit-logged via `record_audit_event()` (previously role changes were
  Django-admin-only and untracked).

`register`, `login`, `refresh`, and the password-reset endpoints carry
`throttle_scope = "auth"` (`DEFAULT_THROTTLE_RATES["auth"]`, default `5/min` via
`AUTH_THROTTLE_RATE`), satisfying the "Rate limiting" security rule.

Added `AUTH_PASSWORD_VALIDATORS` (previously unset, meaning zero password strength
requirements — Django's global default is an empty list, not the usual four
validators).

**Email delivery**: replaced `NoopNotificationAdapter` for the `email` channel with a
real `EmailNotificationAdapter` using `django.core.mail.send_mail` (console backend in
`DEBUG`, SMTP via env vars otherwise) — the minimum needed for verification/reset
emails to actually arrive. `push`/`whatsapp` channels remain no-op; a full Notifications
build-out is a later phase.

### Incidental fix: circular import in `apps.notifications`

Discovered while verifying this work: `apps/notifications/tasks.py` imported
`enqueue_notification` from `notification_orchestrator.py` at module level, which
itself imported `dispatch_notification_task` from `tasks.py` at module level — a
circular import that broke `manage.py check`/`runserver`/any full URL-conf load on the
pre-existing `main` branch. Fixed by moving the `tasks.py` import of
`enqueue_notification` into the two functions that use it (matching this file's
existing pattern of function-local imports for the same reason).

## Consequences

- A web/mobile client can now actually authenticate against this API.
- Every model going forward should inherit `UUIDModel, TimeStampedModel` (and
  `SoftDeleteModel` where deletion must preserve related history) from `apps.common`
  instead of re-declaring the same three fields.
- `apps.common.audit.record_audit_event()` is the standard way to record an audit
  trail; Voting/Governance (Module 11) will depend on this directly.
- Finance webhook ingestion now requires real Stripe/PayPal webhook secrets to be
  configured before any payment can be recorded — there is no more "unauthenticated
  JSON in, ledger entry out" path.
- Migrations were verified against real PostgreSQL (not just SQLite) specifically
  because the `Role` PK issue was invisible on SQLite; this is now the standard for
  verifying any future model retrofit.

## Follow-up

- Migrate `Role.id` to UUID via a dedicated data migration (regenerate ids, repoint
  `identity_user_roles`), if/when full UUID-PK consistency across all models is needed.
- Real push (FCM) and WhatsApp Business API adapters.
- Granular (non-role-level) permission matrix; Django's `Group`/`Permission` framework
  is still unused.
- Family/guardian relationship model (doubles as the Youth Safety module's home).
