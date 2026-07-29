# ADR 0015: Shop↔Finance Payment Linkage and Stock Reservation Timeout

## Status

Accepted

## Context

ADR 0007 shipped inventory-aware order creation but flagged two gaps: shop orders
had no path to an actual payment (a pending order just sat there with no way to
pay it), and reserved stock (decremented at order-creation time) was never
returned to the pool if the order was never paid or was cancelled — a real bug,
not just a missing feature: `transition_order_status` could move an order to
`cancelled` without restoring the inventory it had reserved.

ADR 0014 had just added `apps.finance.application.payment_service.create_checkout_session`
with an `entry_type` parameter and a `reference` stashed in `PaymentTransaction.payload`
specifically so a calling module could be told when its payment succeeded — Shop is
the first consumer of that mechanism.

## Decision

- **Checkout**: `POST /api/shop/orders/{id}/checkout/` (order owner only, order must
  be `pending`) calls `apps.shop.application.order_service.initiate_order_checkout`,
  which calls `apps.finance.application.payment_service.create_checkout_session`
  with `entry_type=shop_sale` and `reference=str(order.payment_reference)` — a
  direct cross-module call, the same precedent as
  `apps.membership.application.tier_service.record_dues_payment` calling into
  `apps.finance.application.ledger_service`.
- **Payment confirmation**: `process_webhook` (ADR 0006/0014), after writing the
  `shop_sale` ledger credit, now calls
  `apps.shop.application.order_service.mark_order_paid_by_reference` with the
  `reference` it captured from the transaction's checkout payload — the reverse
  direction of the same cross-module-call pattern (finance → shop this time,
  mirroring documents → assistant in ADR 0012). `mark_order_paid_by_reference`
  returns `None` instead of raising when no matching pending order is found, since
  a webhook must never fail just because a reference didn't resolve (e.g. a
  donation with no `reference` at all).
- **Stock reservation fixed**: `transition_order_status` now restores each line
  item's `Product.inventory_count` (via an `F()` expression update — race-safe
  without a row lock) whenever an order moves to `cancelled`, from either `pending`
  or `paid`. This was silently missing before; cancelling an order used to leak
  reserved stock permanently.
- **Timeout cancellation**: `apps.shop.application.order_service.cancel_stale_pending_orders`
  cancels (and thus releases inventory for) any `pending` order older than
  `SHOP_ORDER_RESERVATION_TIMEOUT_MINUTES` (default 30). Run every 10 minutes via
  a new Celery beat entry, `apps.shop.tasks.cancel_stale_pending_orders_task`.

## Consequences

- A shop order can now actually be paid for through the same Stripe/PayPal flow
  as donations and membership dues, and the order auto-transitions to `paid` when
  the webhook confirms it — no manual admin step required for the common path
  (`OrderTransitionView` still exists for manual admin overrides).
- Inventory reserved by an order that's abandoned at checkout (browser closed,
  payment never completed) is returned to the pool automatically within
  `SHOP_ORDER_RESERVATION_TIMEOUT_MINUTES`, instead of being lost until a human
  notices and manually adjusts stock.
- Cancelling any order (pending or paid) now correctly restores stock — closing a
  real gap in the original implementation, not just adding new behavior.

## Future considerations

- No shipment tracking/fulfillment events (ADR 0007's other follow-up) — `paid`
  vs `fulfilled` is still a single manual transition with no carrier/tracking
  metadata. Out of scope here; revisit if physical merchandise fulfillment becomes
  a real operational need beyond event merchandise/small goods.
- `cancel_stale_pending_orders` cancels one order at a time in a loop inside a
  single `@transaction.atomic` block; fine at today's order volume, but a very
  large backlog of stale orders would hold that transaction open for a while.
  Batch/paginate if that ever becomes a real volume.
