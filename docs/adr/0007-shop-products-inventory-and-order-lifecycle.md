# ADR 0007: Shop Products, Inventory, and Order Lifecycle

## Status

Accepted

## Context

Phase 4 requires a shop domain with product catalog, inventory control, and order lifecycle to support paid merchandise and related operations.

## Decision

Implement shop bounded context in apps.shop:

- Product entity with SKU, price, active flag, and inventory count.
- ShopOrder and ShopOrderItem entities for order lifecycle and immutable line pricing at order time.
- Order service enforcing inventory checks, stock decrement, and status transitions.
- APIs:
  - GET/POST /api/shop/products/
  - POST /api/shop/orders/
  - GET /api/shop/orders/me/
  - POST /api/shop/orders/transitions/

Role gates:

- product creation: admin or volunteer
- order transition: admin, volunteer, or treasurer

## Consequences

- Inventory is decremented transactionally during order creation.
- Order status flow is explicit and validated.
- Shop can integrate with finance payment workflows without redesign.

## Follow-up

- Add reserved stock and timeout cancellation policy.
- Add shipment tracking and fulfillment events.
- Add payment linkage from shop orders to finance payment transactions.
