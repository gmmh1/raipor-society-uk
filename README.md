# Raipor Society UK Community Operating System

Production-ready, open-source monorepo scaffold for the Raipor Society UK digital ecosystem.

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
git commit -m "chore: bootstrap raipor community os"
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
| 2. Membership | Partial — lifecycle/status transitions, guardian/consent safeguarding gate, dues/tiers, renewal automation, and required DOB at registration done (ADR 0009) |
| 3. Events | Partial — registration, waitlisting, self-cancellation with promotion, QR-scan check-in, event cancellation (soft delete) done (ADR 0010) |
| 4. Notifications | Partial — email delivery real, Celery beat schedule configured; push/WhatsApp adapters outstanding (need a `phone_number` field and, for push, a device-token model) |
| 5. Finance | Partial — ledger, Stripe/PayPal webhook signature verification done; outbound checkout/payment-intent creation, receipts/invoices outstanding |
| 6. Shop | Partial — catalog, inventory-aware orders, soft-deletable products done; Shop↔Finance payment integration outstanding |
| 7. Documents | Not started |
| 8. AI Knowledge Assistant | Not started |
| 9. Chat | Not started |
| 10. Voting | Not started |
| 11. Analytics | Not started |

Web (`web/app`) and mobile (`mobile/`) have no API integration yet regardless of backend module status.

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
