import uuid

from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel
from apps.shop.domain.types import ORDER_PENDING, ORDER_STATUS_CHOICES


class Product(UUIDModel, TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=64, unique=True)
    price_minor = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=8, default="GBP")
    inventory_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "shop_product"
        indexes = [
            models.Index(fields=["is_active", "name"]),
        ]


class ShopOrder(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shop_orders")
    status = models.CharField(max_length=32, choices=ORDER_STATUS_CHOICES, default=ORDER_PENDING)
    total_minor = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=8, default="GBP")
    payment_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        db_table = "shop_order"
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]


class ShopOrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(ShopOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price_minor = models.BigIntegerField(default=0)
    line_total_minor = models.BigIntegerField(default=0)

    class Meta:
        db_table = "shop_order_item"
        constraints = [
            models.UniqueConstraint(fields=["order", "product"], name="uniq_order_product_item"),
        ]
