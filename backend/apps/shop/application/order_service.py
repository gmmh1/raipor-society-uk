from django.db import transaction

from apps.shop.domain.types import ORDER_CANCELLED, ORDER_FULFILLED, ORDER_PAID, ORDER_PENDING
from apps.shop.models import Product, ShopOrder, ShopOrderItem


class ShopError(ValueError):
    pass


@transaction.atomic
def create_order_for_user(*, user, items: list[dict]) -> ShopOrder:
    if not items:
        raise ShopError("Order must include at least one item.")

    order = ShopOrder.objects.create(user=user, status=ORDER_PENDING)
    total = 0
    currency = "GBP"

    for item in items:
        product_id = item["product_id"]
        quantity = int(item["quantity"])
        if quantity <= 0:
            raise ShopError("Quantity must be greater than zero.")

        try:
            product = Product.objects.select_for_update().get(id=product_id, is_active=True)
        except Product.DoesNotExist as exc:
            raise ShopError("Product not found or inactive.") from exc

        if product.inventory_count < quantity:
            raise ShopError(f"Insufficient inventory for product {product.sku}.")

        product.inventory_count -= quantity
        product.save(update_fields=["inventory_count", "updated_at"])

        line_total = product.price_minor * quantity
        ShopOrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price_minor=product.price_minor,
            line_total_minor=line_total,
        )

        total += line_total
        currency = product.currency

    order.total_minor = total
    order.currency = currency
    order.save(update_fields=["total_minor", "currency", "updated_at"])
    return order


@transaction.atomic
def transition_order_status(*, order: ShopOrder, to_status: str) -> ShopOrder:
    allowed = {
        ORDER_PENDING: {ORDER_PAID, ORDER_CANCELLED},
        ORDER_PAID: {ORDER_FULFILLED, ORDER_CANCELLED},
        ORDER_FULFILLED: set(),
        ORDER_CANCELLED: set(),
    }

    if to_status not in allowed.get(order.status, set()):
        raise ShopError(f"Invalid order transition from {order.status} to {to_status}.")

    order.status = to_status
    order.save(update_fields=["status", "updated_at"])
    return order
