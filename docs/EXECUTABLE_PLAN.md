# Executable Build Plan

This plan converts the strategy into implementable engineering milestones with deliverables, acceptance checks, and ownership boundaries.

## Build principles

- Build by module order, one bounded context at a time.
- Keep business logic in application services/use-cases.
- Keep APIs thin and permission-aware.
- Every module ships with tests, docs, and migration strategy.

## Phase 1: Foundation (Weeks 1-4)

### Current progress snapshot

- Shared base models added in `apps.common`: `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel`, and a generic `AuditLog` model with `record_audit_event()`. Existing apps' models retrofitted to inherit these instead of re-declaring the same fields.
- Added ADR: `docs/adr/0008-authentication-foundation-and-security-hardening.md`.

### Deliverables

- Monorepo structure with backend/web/mobile/infra/docs.
- Dockerized local stack: PostgreSQL, Redis, Django, Celery, MinIO, monitoring.
- Django project baseline with health endpoint.
- Next.js web baseline with public, member, and admin route groups.
- CI pipeline for lint and test.
- Secret management baseline with `.env` and `.env.example`.

### Acceptance criteria

- `docker compose up --build -d` runs cleanly.
- Health endpoint returns 200.
- CI passes on a pull request.
- No secrets in git history.

## Phase 2: Identity + RBAC + Membership (Weeks 5-10)

### Current progress snapshot

- Module 1 foundation implemented in `apps.identity` with custom user model, role model, RBAC service, and identity API endpoints.
- Added ADR: `docs/adr/0002-authentication-rbac-boundaries.md`.
- Module 1 real authentication now implemented: JWT login/refresh/logout (`djangorestframework-simplejwt` + token blacklist), registration with email verification, password reset, `auth`-scoped rate limiting, and audited role assign/revoke endpoints. See ADR 0008.
- Module 2 lifecycle foundation implemented in `apps.membership` with transition rules, audit trail, member self-view endpoint, and role-gated transition endpoint.
- Added ADR: `docs/adr/0003-membership-lifecycle-and-audit.md`.
- Youth Safety: `date_of_birth`/`is_minor` on `identity.User`, `GuardianRelationship` model with guardian-recorded consent, and a safeguarding gate in `transition_membership_status` blocking activation of an unconsented minor's membership. Membership dues/tiers (`MembershipTier`, `expires_at`) with dues payments posting to the Finance ledger, plus a `expire_memberships_task` on a newly-configured `CELERY_BEAT_SCHEDULE` (first real beat schedule in this project — the Phase 3 event-reminder tasks are now actually scheduled too). See ADR 0009.
- `date_of_birth` is now a required field on registration (`RegisterRequestSerializer`), rejecting future dates. This closes ADR 0009's follow-up gap: the safeguarding gate is effective for every new member going forward. It remains nullable on `identity.User` for accounts created before this requirement existed.
- Admin/treasurer `GET /api/membership/admin/` list/search endpoint added — paginated (`apps.common.pagination.StandardResultsPagination`), filterable by `status`/`tier`, searchable by username/email/name. Closes ADR 0003's "admin list/search endpoints" follow-up.

### Deliverables

- Custom user model and role hierarchy.
- RBAC policy layer and permission matrix.
- Member profile and membership lifecycle.
- Family and youth-member relationship model.

### Acceptance criteria

- Role-based API access enforced and tested.
- Membership status transitions are auditable.
- Admin workflows for membership are operational.
- Member portal workflow parity between web and mobile for core use-cases.

## Phase 3: Events + Notifications (Weeks 11-14)

### Current progress snapshot

- Module 3 events core implemented in `apps.events` with event model, registration flow, attendance check-in endpoint, and role-based operational gates.
- Added ADR: `docs/adr/0004-events-registration-and-attendance.md`.
- Notifications abstraction implemented in `apps.notifications` with queued delivery model, role-gated send endpoint, and async Celery tasks for event reminders and summaries.
- Added ADR: `docs/adr/0005-notification-abstraction-and-async-jobs.md`.
- Events QR check-in completed (was previously generated but unused — `EventCheckInView` now accepts `qr_token` as well as `registration_id`), waitlisting when capacity is reached, and self-cancellation with automatic oldest-waitlisted promotion. See ADR 0010.
- Notifications real channel adapters completed: Web Push (VAPID, W3C standard — no vendor SDK) via `PushSubscription` + `pywebpush`, and WhatsApp Business Cloud API, both needing the new `identity.User.phone_number` field (settable via `PATCH /api/identity/me/`) and, for push, `PushSubscription` registration endpoints. Retry/backoff (Celery's built-in exponential backoff, `max_retries=5`) and deduplication (`Notification.dedup_key`, partial-unique) also added. See ADR 0013.

### Deliverables

- Event model, registration, attendance, QR check-in.
- Notification service abstraction (email, push, WhatsApp).
- Async jobs for reminders and event summaries.

### Acceptance criteria

- Event registration load-tested for expected demand.
- Notification retries and failure logs in place.
- Public website events and program pages connected to backend data contracts.

## Phase 4: Finance + Shop (Weeks 15-18)

### Current progress snapshot

- Finance core implemented in `apps.finance` with unified ledger entries, payment transaction model, idempotent webhook ingestion, and reconciliation summary API.
- Added ADR: `docs/adr/0006-finance-ledger-payments-and-idempotent-webhooks.md`.
- Finance webhook ingestion hardened: provider-specific endpoints (`/payments/webhooks/stripe/`, `/payments/webhooks/paypal/`) now verify Stripe/PayPal signatures over the raw body before any ledger write (previously `AllowAny` + no verification). See ADR 0008.
- Shop core implemented in `apps.shop` with product catalog, inventory-aware order creation, and role-gated order lifecycle transitions.
- Added ADR: `docs/adr/0007-shop-products-inventory-and-order-lifecycle.md`.
- Shop products and Events now support soft deletion (`deactivate_product`/`cancel_event`) so historical orders/registrations survive a product/event being retired.
- Finance outbound payments completed: `POST /api/finance/payments/checkout/` creates a real Stripe Checkout Session or PayPal v2 order, recording a `pending` `PaymentTransaction` that the existing webhook flow reconciles against by `(provider, external_id)`. PDF receipts (`Receipt`, one-to-one with `LedgerEntry`) generated via WeasyPrint and stored in the same MinIO bucket `apps.documents` uses. Reconciliation summary now includes an automated variance check (ledger credits vs. succeeded payments) with a daily Celery beat task emailing admins/treasurers when flagged. See ADR 0014.
- Shop↔Finance payment integration completed: `POST /api/shop/orders/{id}/checkout/` initiates payment via the same Finance checkout endpoint; the webhook flow transitions the order to `paid` automatically on success. A real bug was also fixed here — cancelling an order never restored its reserved inventory; it now does, and a Celery beat task cancels (and releases stock for) `pending` orders older than `SHOP_ORDER_RESERVATION_TIMEOUT_MINUTES` (default 30). See ADR 0015.

### Deliverables

- Unified ledger domain (donations, fees, sales, expenses, refunds).
- Stripe and PayPal adapters behind payment abstraction.
- Receipt and invoice generation.
- Shop products, inventory, and order lifecycle.

### Acceptance criteria

- Idempotent payment webhook handling.
- Immutable audit trail for financial transactions.
- Reconciliation report endpoint available.

## Phase 5: Documents + AI Assistant (Weeks 19-22)

### Current progress snapshot

- Module 8 (Documents) implemented in `apps.documents`: `Document`/`DocumentVersion` entities
  (immutable, checksummed versions), a three-tier `visibility` access model (public, member,
  staff), title/description/extracted-text search, and a storage abstraction
  (`infrastructure/storage.py`) isolating all MinIO/S3/boto3 usage to one module. Text
  extraction (`infrastructure/extraction.py`, PDF via `pypdf`, images via Tesseract OCR through
  `pytesseract`) runs as an async Celery task after upload, populating `extracted_text` for
  future full-text and, later, RAG chunking. Added ADR:
  `docs/adr/0011-documents-storage-versioning-and-access-control.md`.
- Module 9 (AI Knowledge Assistant) implemented in `apps.assistant`: character-based
  chunking, embeddings via Ollama (`bge-small`), `DocumentChunk` storage with a pgvector
  `VectorField` (384 dimensions, `CREATE EXTENSION vector` via the `VectorExtension()`
  migration operation), cosine-similarity retrieval scoped to the requesting user's
  visible documents (reuses `apps.documents`' `visible_documents_queryset`), and a
  citation-first `POST /api/assistant/query/` endpoint backed by Ollama (`qwen2.5:3b-instruct`).
  Indexing runs as a Celery task chained automatically off `apps.documents`' extraction
  task, and is also re-runnable via `python manage.py reindex_documents`. Every query is
  persisted to `AssistantInteraction` for audit. If retrieval finds no chunks the LLM is
  never called — a fixed "no authorized information" response is returned instead, so the
  assistant cannot answer from memory. Added ADR:
  `docs/adr/0012-ai-knowledge-assistant-rag-pipeline.md`.

### Deliverables

- Document upload/versioning/search with access control.
- OCR ingestion pipeline.
- RAG pipeline with embeddings in pgvector.
- Citation-first assistant endpoint.

### Acceptance criteria

- Assistant never answers outside authorized documents.
- Each answer includes source and location reference.
- Re-index pipeline is repeatable and observable.

## Phase 6: Chat + Voting + Analytics + Launch (Weeks 23-26)

### Current progress snapshot

- Module 10 (Chat) implemented in `apps.chat`: `ChatChannel` (direct/group),
  `ChatChannelMembership`, and an immutable `ChatMessage` (moderation via
  `is_flagged`, never deletion). Youth safety enforced in the application layer —
  a minor's only allowed direct-message counterpart is a supervisor
  (`admin`/`volunteer`), and any group channel containing a minor must include a
  supervisor, checked both at creation and when adding members later. Real-time
  delivery via Django Channels + `channels_redis` + `daphne`, with a custom
  `JWTAuthMiddleware` so WebSocket connections authenticate with the same JWT
  access tokens as the REST API (`wss://.../ws/chat/{channel_id}/?token=...`).
  Added ADR: `docs/adr/0016-chat-realtime-channels-and-youth-safety.md`.
- Module 11 (Voting) implemented in `apps.voting`: `Poll`/`PollOption` plus a
  deliberate split between `PollBallotReceipt` (proves participation, unique per
  poll+user — the actual DB-level duplicate-vote guard) and `PollVote` (the
  tally, with no FK to a user at all, so votes are genuinely anonymous, not just
  hidden). `cast_vote` catches the unique-constraint `IntegrityError` from a
  nested savepoint rather than check-then-act, so duplicate prevention is
  race-safe under concurrent requests. Results are hidden from ordinary members
  until a poll closes; quorum is computed from ballot count. Added ADR:
  `docs/adr/0017-voting-anonymous-secret-ballot-and-quorum.md`.
- Module 12 (Analytics) implemented in `apps.analytics`: no new persisted models
  — every report (`membership_report`, `events_report`, `finance_report`,
  `shop_report`, `documents_report`, `assistant_report`, `chat_report`,
  `voting_report`) is computed live via ORM aggregation over existing tables,
  assembled by `overview_report()` behind a staff-only
  `GET /api/analytics/overview/` endpoint. Added ADR:
  `docs/adr/0018-analytics-live-aggregation-dashboards.md`.

  All 12 backend modules in the build order now have at least a working first
  implementation; see `README.md`'s module status table for per-module detail
  and known follow-ups.

### Deliverables

- Real-time chat channels with youth safety constraints.
- Polling and voting module with anonymity and quorum.
- Analytics dashboards for governance and operations.
- Security hardening, backups, and launch checklist.

### Acceptance criteria

- Duplicate voting blocked at database level.
- Vote tampering protection via immutable audit records.
- Backup and restore drill documented and verified.

## Module execution template

For each module, execute this checklist:

1. Write ADR and domain boundaries.
2. Define entities, use-cases, and repository interfaces.
3. Implement migrations and indexes.
4. Implement service layer and API layer.
5. Add unit and integration tests.
6. Add admin workflows and audit logs.
7. Update docs and run deployment checks.
