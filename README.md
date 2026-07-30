# Raipur Society UK Community Operating System

Production-ready, open-source monorepo scaffold for the Raipur Society UK digital ecosystem.

## What this repository sets up

- Django backend API with clean architecture boundaries (domain/application/infrastructure/presentation)
- PostgreSQL + Redis + Celery foundation
- Docker-first local and deployment workflow
- Next.js web frontend (public site + member portal + admin portal)
- Expo React Native mobile shell
- MinIO object storage
- AI runtime placeholder with Ollama + RAG settings
- Monitoring stack (Prometheus, Grafana, Loki)
- GitHub CI pipeline and issue templates
- Vercel web deployment and Cloudflare domain/edge blueprint
- Executable module roadmap aligned to your plan

## Repository layout

```text
backend/            Django API, domain apps, tests
web/                Next.js website, member portal, admin portal
mobile/             Expo React Native shell
infra/              Docker, reverse proxy, monitoring config
.github/            CI workflow and issue templates
docs/               Architecture decisions and execution plan
scripts/            Bootstrap and helper scripts
```

## Quick start (local)

1. Clone and open the repo.
2. Review and update `.env` values.
3. Build and start services:

```bash
docker compose up --build -d
```

4. Run database migrations:

```bash
docker compose exec backend python manage.py migrate
```

5. Create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

6. Open services:

- API: http://localhost:8000/api/health/
- Admin: http://localhost:8000/admin/
- Grafana: http://localhost:3000
- MinIO Console: http://localhost:9001

## Git + GitHub setup

```bash
git init
git add .
git commit -m "chore: bootstrap raipur community os"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Environment and credentials

- `.env` is included for immediate local bootstrapping.
- Real API credentials must be set before enabling Stripe/PayPal/WhatsApp in production.
- `.env` is ignored by git; `.env.example` is safe to commit.

## Development standards

- Keep business logic in service/use-case layers.
- Add tests for each module increment.
- Avoid vendor lock-in and paid dependencies where open-source alternatives exist.
- Track architecture decisions in `docs/adr/`.

## Module status

Follow [docs/EXECUTABLE_PLAN.md](docs/EXECUTABLE_PLAN.md) for full deliverables/acceptance criteria per phase. Current state:

| Module | Status |
|---|---|
| 1. Authentication + RBAC | Done — JWT login/refresh/logout, registration + email verification, password reset, rate limiting, audited role assignment (ADR 0002, 0008) |
| 2. Membership | Done — lifecycle/status transitions, guardian/consent safeguarding gate, dues/tiers, renewal automation, required DOB at registration, admin list/search with pagination and filtering (ADR 0009). Self-registration now creates a `Membership` row for the new user immediately (previously only created on first "My Membership" view, so newly registered members didn't show up in the admin Membership list until they logged in and visited it themselves); `backfill_memberships` management command exists for any accounts created before this fix. |
| 3. Events | Done — registration, waitlisting, self-cancellation with promotion, QR-scan check-in, event cancellation (soft delete) (ADR 0010). Admin can create/list/cancel events from `/admin/events`; public `/events` page renders live upcoming events instead of a static placeholder. |
| 4. Notifications | Done — email delivery real, Web Push (VAPID) and WhatsApp Business API adapters, retry/backoff with dead-letter status, deduplication keys, Celery beat schedule configured (ADR 0013) |
| 5. Finance | Done — ledger, Stripe/PayPal webhook signature verification, outbound Stripe/PayPal checkout, PDF receipts (WeasyPrint), daily reconciliation-variance alerting (ADR 0014) |
| 6. Shop | Done — catalog, inventory-aware orders, soft-deletable products, Shop↔Finance checkout linkage, stock-reservation timeout cancellation (ADR 0015). Products support an optional `image_url` and a comma-separated `available_sizes` list (e.g. "S,M,L,XL"); inventory is still tracked per-product, not per-size. Order line items record the chosen size. |
| 7. Documents | Done — upload/versioning with checksums, three-tier visibility access control, title/description/extracted-text search, MinIO storage abstraction, async PDF/OCR text extraction (ADR 0011) |
| 8. AI Knowledge Assistant | Done — chunking, Ollama/BGE embeddings, pgvector storage, permission-scoped cosine retrieval, citation-first query endpoint, audit trail, re-index management command (ADR 0012); no ANN index or conversation memory yet |
| 9. Chat | Done — real-time channels (Django Channels + channels_redis + daphne), JWT-authenticated WebSockets, direct/group channels, immutable messages with flag-based moderation, youth-safety rules restricting minors' direct messages and group membership to supervised contexts (ADR 0016) |
| 10. Voting | Done — anonymous secret-ballot polls (participation and choice recorded in separate tables with no linking FK), database-level duplicate-vote prevention via a unique constraint + IntegrityError handling, quorum tracking, results hidden until close (ADR 0017) |
| 11. Analytics | Done — staff-only governance/operations dashboard (`GET /api/analytics/overview/`), live ORM aggregation across all other modules with no separate reporting tables (ADR 0018) |
| 12. Blog / News | Done — native Django app (`apps.blog`, not django-cms/djangocms-blog — see below), draft/publish workflow with slug auto-generation, soft-delete. Public `/blog` listing + `/blog/[slug]` detail pages; admin management at `/admin/blog` (create, publish/unpublish, delete). |

Web (`web/app`) now has real, API-backed Member and Admin portals (auth, live data, real actions) alongside the public marketing site. Mobile (`mobile/`) still has no API integration.

**Why not djangocms-blog for the Blog/News module:** it requires `django-cms>=3.9,<4.0` plus `django-parler`, `django-filer`, `django-taggit`, and `djangocms-text-ckeditor` — an entire separate, server-rendered CMS framework with its own page tree and template placeholders, incompatible with this project's headless DRF API + Next.js/React Native frontend split. A native module (same Clean Architecture pattern as every other app here) gets the same outcome — an admin CMS for posts — without forking the architecture in two directions.

## Web deployment references

- Vercel + Cloudflare runbook: [docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md](docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md)
- Web feature matrix: [docs/WEB_FEATURE_MATRIX.md](docs/WEB_FEATURE_MATRIX.md)

## Local model continuation (Qwen2.5-Coder)

Use this workflow to let a local model continue the same project with the same architecture constraints:

1. Generate handoff context (Windows-native):

```powershell
pwsh -File scripts/export-local-handoff.ps1
```

Optional (if `make` is installed):

```bash
make local-handoff
```

2. Generate handoff context and a ready starter prompt in one step (Windows-native):

```powershell
pwsh -File scripts/local-qwen-session.ps1
```

Optional (if `make` is installed):

```bash
make local-qwen
```

3. Load these files into your local coding model session:

- `CLAUDE.md`
- `docs/EXECUTABLE_PLAN.md`
- `docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md`
- `docs/QWEN_LOCAL_SYSTEM_PROMPT.md`
- `docs/LOCAL_MODEL_SESSION_CONTEXT.md`
- `docs/LOCAL_MODEL_START_PROMPT.md` (if generated)

4. Follow the full guide:

- [docs/LOCAL_MODEL_CONTINUATION.md](docs/LOCAL_MODEL_CONTINUATION.md)
