from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.finance.domain.types import (
    DIRECTION_CHOICES,
    ENTRY_TYPE_CHOICES,
    PAYMENT_PENDING,
    PAYMENT_STATUS_CHOICES,
    PROVIDER_CHOICES,
)


class LedgerEntry(UUIDModel):
    entry_type = models.CharField(max_length=32, choices=ENTRY_TYPE_CHOICES)
    direction = models.CharField(max_length=16, choices=DIRECTION_CHOICES)
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=8, default="GBP")
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ledger_entries_recorded",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "finance_ledger_entry"
        indexes = [
            models.Index(fields=["entry_type", "created_at"]),
            models.Index(fields=["currency"]),
        ]


class PaymentTransaction(UUIDModel, TimeStampedModel):
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    external_id = models.CharField(max_length=128)
    status = models.CharField(max_length=32, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    amount_minor = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=8, default="GBP")
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_transactions",
    )
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "finance_payment_transaction"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_id"], name="uniq_payment_provider_external"
            ),
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]


class Receipt(UUIDModel, TimeStampedModel):
    """A PDF receipt for a completed ledger credit (donation, dues, shop sale).

    ``receipt_number`` is derived from the row's own id rather than a sequential
    counter — see ADR 0014. Not suitable as a VAT invoice number if the charity
    ever becomes VAT-registered.
    """

    ledger_entry = models.OneToOneField(
        LedgerEntry, on_delete=models.PROTECT, related_name="receipt"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="receipts",
    )
    receipt_number = models.CharField(max_length=32, unique=True)
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=8, default="GBP")
    description = models.CharField(max_length=255, blank=True)
    pdf_file_key = models.CharField(max_length=512)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="receipts_issued",
    )

    class Meta:
        db_table = "finance_receipt"
        indexes = [
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.receipt_number


class PaymentWebhookEvent(UUIDModel):
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    event_id = models.CharField(max_length=128)
    event_type = models.CharField(max_length=128, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "finance_payment_webhook_event"
        constraints = [
            models.UniqueConstraint(fields=["provider", "event_id"], name="uniq_webhook_provider_event"),
        ]
        indexes = [
            models.Index(fields=["provider", "received_at"]),
        ]
