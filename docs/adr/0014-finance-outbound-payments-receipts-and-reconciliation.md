# ADR 0014: Finance Outbound Payments, Receipts, and Reconciliation Variance

## Status

Accepted

## Context

ADR 0006 shipped inbound webhook ingestion (a payment made elsewhere lands as a
webhook) with signature verification added later. Its follow-up flagged three
gaps: nothing in the backend could actually *start* a Stripe/PayPal payment, there
was no receipt/invoice generation, and reconciliation had no automated variance
detection — `reconciliation_summary()` just listed totals for a human to eyeball.

## Decision

- **Outbound checkout**: `POST /api/finance/payments/checkout/` (any authenticated
  user — donations aren't role-gated) calls
  `apps.finance.application.payment_service.create_checkout_session`, which creates
  a Stripe Checkout Session or a PayPal v2 order (new functions in
  `infrastructure/payment_adapters.py`, the same module that already isolates all
  Stripe/PayPal SDK usage) and records a `PaymentTransaction` with `status=pending`
  before redirecting the payer. The `entry_type` (donation/membership_fee/shop_sale)
  and `reference` the payer selected are stashed in `PaymentTransaction.payload` at
  creation time. When the webhook later arrives, `process_webhook` now reads that
  stashed `entry_type` *before* overwriting `payload` with the raw webhook body, so
  the resulting `LedgerEntry.entry_type` reflects what was actually being paid for
  instead of always defaulting to `donation` — this was a real bug fixed as part of
  this change, not a hypothetical.
- **Receipts**: `Receipt` (one-to-one with `LedgerEntry`) is generated via
  `apps.finance.application.receipt_service.issue_receipt`, rendered from a Django
  template through WeasyPrint (`infrastructure/pdf.py`, per `CLAUDE.md`'s
  preference for WeasyPrint over a paid PDF API), and stored in the same MinIO
  bucket as documents by directly reusing
  `apps.documents.infrastructure.storage` — the same cross-app-infra-reuse pattern
  ADR 0012 already established rather than duplicating an S3 client. Issuance is
  manual via `POST /api/finance/receipts/` (admin/treasurer), not automatic on
  every successful webhook — auto-issuing for every ledger credit (including ones
  that don't need a receipt, like an internal expense reversal) would be the wrong
  default; see Future considerations.
  `receipt_number` is derived from the receipt's own UUID
  (`RCT-YYYYMMDD-<8 hex chars>`), not a sequential counter — see Future
  considerations for why this isn't VAT-invoice-safe.
- **Reconciliation variance**: `reconciliation_summary()` now also returns
  `payment_derived_ledger_credit_minor`, `succeeded_payment_transactions_minor`,
  `variance_minor`, and `variance_flagged` — comparing ledger credits for
  payment-derived entry types against succeeded `PaymentTransaction` totals per
  currency. A new daily Celery beat task,
  `apps.finance.tasks.check_reconciliation_variance_task`, calls this and emails
  every admin/treasurer when a variance is flagged, using a date-scoped
  `dedup_key` (`reconciliation-variance-{currency}-{date}`) so a beat restart
  can't double-send same-day but an unresolved variance still re-alerts the next
  day.
- **Full double-entry bookkeeping was explicitly not implemented.** `LedgerEntry`
  remains single-sided (one row per debit or credit, not matched debit/credit
  pairs). Redesigning it into true double-entry would touch every ledger-writing
  call site across `apps.membership` (dues), `apps.shop` (sales), and
  `apps.finance` itself (webhooks, manual entries) — a large, risky migration for
  a charity-scale ledger where the acceptance criteria (idempotent webhooks,
  immutable audit trail, a reconciliation report) are already met without it. The
  variance check above gives the practical benefit (catching drift) without the
  schema risk.

## Consequences

- The platform can now originate a payment, not just receive a webhook for one
  made through an out-of-band link — donations, membership dues, and shop
  checkout can all go through the same `payments/checkout/` endpoint.
- Supporters and members get a real PDF receipt on request, stored durably in
  object storage with a presigned download URL, access-controlled to the
  recipient or admin/treasurer.
- Reconciliation drift (a webhook that succeeded without a ledger entry, or a
  manual ledger entry with no matching payment) is now caught automatically
  within a day instead of only being visible if a treasurer happens to inspect
  the summary endpoint.

## Future considerations

- `receipt_number` is not sequential and is not appropriate as a VAT invoice
  number. If the charity becomes VAT-registered, a properly sequential,
  gap-free numbering scheme (a locked counter, not a UUID-derived string) would
  be required.
- Receipts are issued manually, not automatically on every successful payment.
  Auto-issuing on `PAYMENT_SUCCEEDED` for donation/membership_fee/shop_sale
  entries specifically (not every ledger credit) would remove a manual step but
  needs a decision on whether every donor wants a receipt emailed automatically
  vs. requesting one — a product question, not just an engineering one.
- No true double-entry ledger (see Decision). Revisit if a real accountant
  requirement (e.g. formal statutory accounts prep) needs matched debit/credit
  pairs rather than the current single-sided model plus variance checking.
- `check_reconciliation_variance_task` currently only checks `GBP`
  (`RECONCILED_CURRENCIES` in `apps/finance/tasks.py`) — extend that tuple if
  multi-currency ledger activity becomes real rather than theoretical.
