# Generated manually to match finance models where Django CLI is unavailable.

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
            name="LedgerEntry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "entry_type",
                    models.CharField(
                        choices=[
                            ("donation", "Donation"),
                            ("membership_fee", "Membership Fee"),
                            ("shop_sale", "Shop Sale"),
                            ("expense", "Expense"),
                            ("refund", "Refund"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "direction",
                    models.CharField(
                        choices=[("debit", "Debit"), ("credit", "Credit")],
                        max_length=16,
                    ),
                ),
                ("amount_minor", models.BigIntegerField()),
                ("currency", models.CharField(default="GBP", max_length=8)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("reference", models.CharField(blank=True, max_length=128)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recorded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="ledger_entries_recorded",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "finance_ledger_entry",
                "indexes": [
                    models.Index(fields=["entry_type", "created_at"], name="finance_led_entry_t_914952_idx"),
                    models.Index(fields=["currency"], name="finance_led_currency_720267_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "provider",
                    models.CharField(
                        choices=[("stripe", "Stripe"), ("paypal", "PayPal"), ("manual", "Manual")],
                        max_length=32,
                    ),
                ),
                ("external_id", models.CharField(max_length=128)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("amount_minor", models.BigIntegerField(default=0)),
                ("currency", models.CharField(default="GBP", max_length=8)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "payer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="payment_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "finance_payment_transaction",
                "indexes": [models.Index(fields=["status", "created_at"], name="finance_pay_status_8f1d6f_idx")],
                "constraints": [
                    models.UniqueConstraint(fields=("provider", "external_id"), name="uniq_payment_provider_external")
                ],
            },
        ),
        migrations.CreateModel(
            name="PaymentWebhookEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "provider",
                    models.CharField(
                        choices=[("stripe", "Stripe"), ("paypal", "PayPal"), ("manual", "Manual")],
                        max_length=32,
                    ),
                ),
                ("event_id", models.CharField(max_length=128)),
                ("event_type", models.CharField(blank=True, max_length=128)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "finance_payment_webhook_event",
                "indexes": [models.Index(fields=["provider", "received_at"], name="finance_pay_provider_eb16f8_idx")],
                "constraints": [
                    models.UniqueConstraint(fields=("provider", "event_id"), name="uniq_webhook_provider_event")
                ],
            },
        ),
    ]
