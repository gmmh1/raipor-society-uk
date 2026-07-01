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

## Next implementation targets

Follow [docs/EXECUTABLE_PLAN.md](docs/EXECUTABLE_PLAN.md) in sequence:

1. Authentication + RBAC
2. Membership
3. Events
4. Notifications
5. Finance
6. Shop
7. Documents
8. AI Knowledge Assistant
9. Chat
10. Voting
11. Analytics

## Web deployment references

- Vercel + Cloudflare runbook: [docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md](docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md)
- Web feature matrix: [docs/WEB_FEATURE_MATRIX.md](docs/WEB_FEATURE_MATRIX.md)

## Local model continuation (Qwen2.5-Coder)

Use this workflow to let a local model continue the same project with the same architecture constraints:

1. Generate handoff context:

```bash
make local-handoff
```

Or generate handoff context and a ready starter prompt in one step:

```bash
make local-qwen
```

2. Load these files into your local coding model session:

- `CLAUDE.md`
- `docs/EXECUTABLE_PLAN.md`
- `docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md`
- `docs/QWEN_LOCAL_SYSTEM_PROMPT.md`
- `docs/LOCAL_MODEL_SESSION_CONTEXT.md`
- `docs/LOCAL_MODEL_START_PROMPT.md` (if generated with `make local-qwen`)

3. Follow the full guide:

- [docs/LOCAL_MODEL_CONTINUATION.md](docs/LOCAL_MODEL_CONTINUATION.md)
