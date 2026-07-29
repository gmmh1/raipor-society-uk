# ADR 0013: Notifications Real Channels, Retry, and Deduplication

## Status

Accepted

## Context

ADR 0005 shipped the notification abstraction with a real email adapter and no-op
stand-ins for push and WhatsApp. ADR 0010's follow-up flagged that push needed a
device-token model and WhatsApp needed a `phone_number` field, neither of which
existed. ADR 0005 also deferred retry/backoff and deduplication.

## Decision

- **`phone_number`** added to `identity.User` (blank-by-default `CharField`, no format
  enforcement — international numbers vary too much for a single regex to be worth
  the false rejections). `GET/PATCH /api/identity/me/` (`current_user_view`, now
  accepting `PATCH`) lets a user set their own phone number.
- **Push**: implemented as **Web Push (VAPID)**, a W3C standard, rather than a vendor
  SDK (Firebase Cloud Messaging, APNs) — consistent with `CLAUDE.md`'s "avoid vendor
  lock-in" and "zero unnecessary licensing costs" preferences, and it works for any
  modern browser without a paid account. `PushSubscription` stores one row per
  registered browser/device (`endpoint`, `p256dh_key`, `auth_key`, `is_active`).
  `POST /api/notifications/push-subscriptions/` registers/refreshes a subscription
  (`update_or_create` on `endpoint`); `POST .../unregister/` deactivates it.
  `WebPushNotificationAdapter` sends to every active subscription for the recipient
  via `pywebpush`; a `404`/`410` response (subscription expired/gone) deactivates
  that row automatically rather than retrying it forever. Native mobile push
  (FCM/APNs) is out of scope — see Future considerations.
- **WhatsApp**: implemented against the WhatsApp Business Cloud API (Meta) via
  `WhatsAppNotificationAdapter`, isolated to one module exactly like
  `apps.finance.infrastructure.payment_adapters` isolates Stripe/PayPal. This is a
  deliberate, acknowledged exception to "avoid vendor lock-in" — there is no
  self-hosted, open-source WhatsApp send API; WhatsApp itself is the requirement.
- **Retry/backoff**: `dispatch_notification` now raises on adapter failure (after
  recording `status=failed` + `error_message` for that attempt) instead of
  swallowing the exception. `dispatch_notification_task` is now `bind=True` with
  Celery's built-in `retry_backoff` (exponential, capped at 600s, jittered),
  `max_retries=5`, and calls `self.retry(exc=exc)` on failure. A `Notification.attempts`
  counter tracks how many delivery attempts have been made.
- **Dead-letter handling**: no separate dead-letter table. After `max_retries` is
  exhausted, Celery re-raises and the row is left in its last-recorded `failed`
  state with `error_message` populated — that terminal state, filterable via the
  existing `status` field (and visible in `NotificationAdmin`), *is* the dead
  letter. A dedicated DLQ model would duplicate what `status=failed` already gives
  us for a system operating at this volume.
- **Deduplication**: `Notification.dedup_key` (blank by default, partial unique
  constraint enforced only when non-empty via `condition=~Q(dedup_key="")`).
  `queue_notification(..., dedup_key=...)` returns the existing row instead of
  creating a duplicate if one already exists in `queued` or `sent` state for that
  key — callers that fire the same logical notification more than once (e.g. a
  reminder task re-run) get exactly one delivery, not several.

## Consequences

- Push notifications work today, for free, on any browser that supports the Web
  Push standard — no Firebase/APNs account or cost required.
- WhatsApp delivery requires a Meta Business API token in production; local/dev
  environments simply leave `WHATSAPP_API_TOKEN` unset and the adapter fails loudly
  (caught by the retry/dead-letter path) rather than silently no-opping, so a
  misconfiguration is visible in `Notification.error_message`.
- Transient failures (a provider hiccup, a momentarily-down webhook) now
  self-heal via retry instead of being permanently marked failed on the first
  attempt.
- Re-running a task that enqueues the same logical notification twice (e.g. Celery
  beat firing twice due to a worker restart) is now safe when the caller supplies a
  `dedup_key`.

## Future considerations

- Native mobile push (FCM/APNs) is not implemented. If the Expo mobile app needs
  background push beyond what a mobile browser's Web Push support provides,
  Expo's own push service (which itself sits on FCM/APNs) would need to be
  evaluated against the vendor-lock-in principle at that time.
- `phone_number` has no format validation or verification (no SMS OTP confirming
  the number is real/owned by the user) — acceptable for WhatsApp delivery today,
  but would need hardening if `phone_number` is ever used for anything
  security-sensitive (e.g. 2FA).
- No per-user notification preferences (opt out of a channel) yet — every channel
  a recipient has an address/subscription/token for is eligible to receive
  whatever gets enqueued to it.
