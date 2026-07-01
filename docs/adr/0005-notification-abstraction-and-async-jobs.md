# ADR 0005: Notification Abstraction and Async Jobs

## Status

Accepted

## Context

Phase 3 requires a notification abstraction and asynchronous jobs for reminders and post-event summaries, while preserving open-source and self-hosted constraints.

## Decision

Implement `apps.notifications` as the messaging abstraction layer:

- `Notification` entity stores channel, payload, status, and delivery timestamps.
- Channel and delivery states defined in `apps.notifications.domain.types`.
- Delivery abstraction in `apps.notifications.infrastructure.adapters` with a no-op adapter baseline.
- Queue + dispatch workflow in `apps.notifications.application`.
- Celery tasks:
  - `dispatch_notification_task`
  - `enqueue_event_reminders_task`
  - `enqueue_event_summary_task`
- API endpoints:
  - `GET /api/notifications/me/`
  - `POST /api/notifications/send/` (admin/volunteer)

Events and membership services now enqueue email notifications for key lifecycle changes.

## Consequences

- Downstream channel adapters can be introduced without changing domain/application contracts.
- Notification delivery remains asynchronous and resilient to temporary channel failures.
- Event and membership workflows now emit user-facing notifications by default.

## Follow-up

- Implement real adapters for SMTP, push provider, and WhatsApp provider.
- Add retry/backoff policy and dead-letter handling.
- Add deduplication keys for idempotent sends.
