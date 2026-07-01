# ADR 0004: Events Registration and Attendance Core

## Status

Accepted

## Context

Module 3 requires event management, registration, and attendance tracking with role-gated operational actions and member eligibility checks.

## Decision

Implement events as a bounded context in `apps.events` with clean-architecture separation:

- `Event` entity for scheduling/publication/capacity.
- `EventRegistration` entity for attendee lifecycle and QR token.
- Domain status constants in `apps.events.domain.status`.
- Registration and check-in use-cases in `apps.events.application.event_service`.
- API transport in `apps.events.presentation` with thin orchestration.

Routes:

- `GET /api/events/` (published events)
- `POST /api/events/` (admin/volunteer only)
- `POST /api/events/register/` (authenticated active members)
- `POST /api/events/attendance/check-in/` (admin/volunteer only)

## Consequences

- Event registration now enforces publication state, capacity, and active membership.
- Attendance check-in is traceable via registration status and check-in actor/timestamp.
- Downstream notification workflows can subscribe to registration/check-in events.

## Follow-up

- Add cancellation endpoint and waitlist support.
- Add QR payload signing for scanner validation.
- Add notification jobs for reminders and post-event summaries.
