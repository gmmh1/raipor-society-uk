# Executable Build Plan

This plan converts the strategy into implementable engineering milestones with deliverables, acceptance checks, and ownership boundaries.

## Build principles

- Build by module order, one bounded context at a time.
- Keep business logic in application services/use-cases.
- Keep APIs thin and permission-aware.
- Every module ships with tests, docs, and migration strategy.

## Phase 1: Foundation (Weeks 1-4)

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
- Module 2 lifecycle foundation implemented in `apps.membership` with transition rules, audit trail, member self-view endpoint, and role-gated transition endpoint.
- Added ADR: `docs/adr/0003-membership-lifecycle-and-audit.md`.

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

### Deliverables

- Event model, registration, attendance, QR check-in.
- Notification service abstraction (email, push, WhatsApp).
- Async jobs for reminders and event summaries.

### Acceptance criteria

- Event registration load-tested for expected demand.
- Notification retries and failure logs in place.
- Public website events and program pages connected to backend data contracts.

## Phase 4: Finance + Shop (Weeks 15-18)

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
