# ADR 0006: Finance Ledger, Payments, and Idempotent Webhooks

## Status

Accepted

## Context

Phase 4 requires a unified finance domain with auditable ledger entries, payment provider abstraction, and idempotent webhook handling.

## Decision

Implement finance bounded context in apps.finance:

- LedgerEntry for immutable financial movements with direction and type.
- PaymentTransaction for normalized provider transaction state.
- PaymentWebhookEvent for webhook idempotency using unique provider plus event_id.
- Payment adapter parser abstraction in infrastructure layer.
- Application services:
  - ledger write service
  - webhook processing service
  - reconciliation summary service
- APIs:
  - POST /api/finance/ledger/entries/
  - GET /api/finance/ledger/
  - POST /api/finance/payments/webhooks/
  - GET /api/finance/reconciliation/summary/

## Consequences

- Financial records are centralized and queryable for reconciliation.
- Duplicate webhook deliveries do not duplicate transactions or ledger writes.
- Provider-specific payload parsing is isolated from core services.

## Follow-up

- Add Stripe and PayPal signature verification.
- Add invoice and receipt entities with PDF generation.
- Add double-entry balancing checks and reconciliation variance alerts.
