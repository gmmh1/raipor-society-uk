# Generated manually for shop models where Django CLI is unavailable.

import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sku", models.CharField(max_length=64, unique=True)),
                ("price_minor", models.BigIntegerField(default=0)),
                ("currency", models.CharField(default="GBP", max_length=8)),
                ("inventory_count", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "shop_product",
                "indexes": [models.Index(fields=["is_active", "name"], name="shop_produc_is_acti_8d609d_idx")],
            },
        ),
        migrations.CreateModel(
            name="ShopOrder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("paid", "Paid"),
                            ("fulfilled", "Fulfilled"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("total_minor", models.BigIntegerField(default=0)),
                ("currency", models.CharField(default="GBP", max_length=8)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="shop_orders", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "shop_order",
                "indexes": [models.Index(fields=["status", "created_at"], name="shop_order_status_8b37aa_idx")],
            },
        ),
        migrations.CreateModel(
            name="ShopOrderItem",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("unit_price_minor", models.BigIntegerField(default=0)),
                ("line_total_minor", models.BigIntegerField(default=0)),
                (
                    "order",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="items", to="shop.shoporder"),
                ),
                (
                    "product",
                    models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="order_items", to="shop.product"),
                ),
            ],
            options={
                "db_table": "shop_order_item",
                "constraints": [
                    models.UniqueConstraint(fields=("order", "product"), name="uniq_order_product_item")
                ],
            },
        ),
    ]
