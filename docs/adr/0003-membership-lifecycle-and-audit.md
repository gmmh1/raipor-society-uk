# ADR 0003: Membership Lifecycle and Audit Trail

## Status

Accepted

## Context

Module 2 in the roadmap requires membership lifecycle management with explicit transitions, role-gated administration, and auditable status changes.

## Decision

Implement membership lifecycle as a dedicated bounded context in `apps.membership`:

- `Membership`: one-to-one record with identity user, status, and lifecycle timestamps.
- `MembershipStatusTransition`: append-only audit log for status changes.
- Transition rules encoded in `apps.membership.domain.status`.
- Lifecycle service (`apps.membership.application.lifecycle_service`) enforces allowed transitions and writes audit entries.
- Admin/treasurer role gate on transition endpoint via `HasAnyRole`.

API endpoints:

- `GET /api/membership/me/`
- `POST /api/membership/transitions/`

## Consequences

- Membership business logic is isolated from transport and persistence details.
- Every status change is traceable with actor, from/to status, reason, and timestamp.
- Future modules can consume a stable lifecycle contract for downstream workflows.

## Follow-up

- Add workflow notifications on transition events.
- Add policy rules for automatic expiration/renewal.
- Add admin list/search endpoints with pagination and filtering.
