from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from apps.shop.domain.types import ORDER_CANCELLED, ORDER_FULFILLED, ORDER_PAID, ORDER_PENDING
from apps.shop.models import Product, ShopOrder, ShopOrderItem


class ShopError(ValueError):
    pass


@transaction.atomic
def deactivate_product(*, product: Product) -> Product:
    """Soft-delete a product. Historical ShopOrderItem rows are preserved via PROTECT."""
    product.is_active = False
    product.save(update_fields=["is_active", "updated_at"])
    product.delete()  # SoftDeleteModel.delete() sets deleted_at, does not remove the row
    return product


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

    if to_status == ORDER_CANCELLED:
        _restore_inventory(order)

    order.status = to_status
    order.save(update_fields=["status", "updated_at"])
    return order


def _restore_inventory(order: ShopOrder) -> None:
    """Returns each line item's quantity to stock. Inventory is decremented at order
    creation time (that *is* the reservation), so cancelling — whether by an explicit
    transition or the stale-order timeout task — must give it back. Uses an F()
    expression update (race-safe on its own) rather than a row lock.
    """
    for item in order.items.all():
        Product.objects.filter(id=item.product_id).update(
            inventory_count=models.F("inventory_count") + item.quantity
        )


def initiate_order_checkout(
    *, order: ShopOrder, provider: str, payer, success_url: str, cancel_url: str
) -> dict:
    """Starts an outbound Stripe/PayPal payment for a pending order's total.

    Cross-module call into ``apps.finance`` — the same direct-call precedent as
    ``apps.membership.application.tier_service.record_dues_payment`` posting to the
    finance ledger. See ADR 0015.
    """
    from apps.finance.application.payment_service import create_checkout_session
    from apps.finance.domain.types import ENTRY_TYPE_SHOP_SALE

    if order.status != ORDER_PENDING:
        raise ShopError(f"Order must be pending to start checkout (is '{order.status}').")

    return create_checkout_session(
        provider=provider,
        amount_minor=order.total_minor,
        currency=order.currency,
        entry_type=ENTRY_TYPE_SHOP_SALE,
        description=f"Shop order {order.id}",
        reference=str(order.payment_reference),
        payer=payer,
        success_url=success_url,
        cancel_url=cancel_url,
    )


@transaction.atomic
def mark_order_paid_by_reference(*, payment_reference: str) -> ShopOrder | None:
    """Called from ``apps.finance``'s webhook processing when a ``shop_sale`` payment
    succeeds, to transition the matching order out of ``pending``. Returns ``None``
    (rather than raising) when no matching pending order exists, since webhook
    processing must not fail just because a reference didn't resolve.
    """
    try:
        order = ShopOrder.objects.select_for_update().get(
            payment_reference=payment_reference, status=ORDER_PENDING
        )
    except (ShopOrder.DoesNotExist, ValueError):
        return None

    order.status = ORDER_PAID
    order.save(update_fields=["status", "updated_at"])
    return order


@transaction.atomic
def cancel_stale_pending_orders() -> int:
    """Cancels pending orders older than ``SHOP_ORDER_RESERVATION_TIMEOUT_MINUTES``
    and releases their reserved inventory. See ADR 0015.
    """
    cutoff = timezone.now() - timezone.timedelta(
        minutes=settings.SHOP_ORDER_RESERVATION_TIMEOUT_MINUTES
    )
    stale_orders = ShopOrder.objects.select_for_update().filter(
        status=ORDER_PENDING, created_at__lt=cutoff
    )

    count = 0
    for order in stale_orders:
        transition_order_status(order=order, to_status=ORDER_CANCELLED)
        count += 1
    return count
