# ADR 0002: Authentication and RBAC Boundaries

## Status

Accepted

## Context

Module 1 in the executable roadmap requires authentication and role-based access control as a foundation for all downstream modules.

The project must keep business rules outside transport and UI layers, and provide maintainable boundaries for future modules.

## Decision

We implement authentication and RBAC in `apps.identity` with explicit clean-architecture layering:

- `apps.identity.models`: persistence entities (`User`, `Role`) with no business-rule logic
- `apps.identity.application.rbac_service`: RBAC decision functions
- `apps.identity.presentation.serializers` and `apps.identity.presentation.views`: API transport layer
- `apps.identity.permissions`: reusable DRF permission class for role gates

API endpoints:

- `GET /api/identity/me/`
- `POST /api/identity/rbac/check/`

Django settings now use a custom user model:

- `AUTH_USER_MODEL = "identity.User"`

## Consequences

- Future modules (membership/events/finance) can depend on stable RBAC services and permission classes.
- User identity now uses UUID primary keys and audit timestamps.
- Database migration required before running app in persistent environments.

## Follow-up

- Add JWT/OAuth strategy (while preserving RBAC service contract).
- Add seeded baseline roles and permission matrix per module.
- Add object-level permissions for sensitive records.
