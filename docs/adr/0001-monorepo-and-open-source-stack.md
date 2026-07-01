# ADR 0001: Monorepo and Open-Source Stack

## Status

Accepted

## Context

The platform must be maintainable by future volunteers with minimal recurring cost and no hard dependency on paid SaaS.

## Decision

Adopt a monorepo with:

- Django + DRF + Celery backend
- PostgreSQL + Redis + MinIO
- Expo React Native mobile shell
- Docker-first deployment and local development
- Open observability stack (Prometheus, Grafana, Loki)

## Consequences

### Positive

- Reduced operational complexity
- Easier contributor onboarding
- Clear system boundaries
- Lower cost and reduced vendor lock-in

### Trade-offs

- Requires careful dependency management
- CI must support multi-surface validation
