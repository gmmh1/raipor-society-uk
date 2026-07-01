from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.finance.domain.types import (
    DIRECTION_CREDIT,
    ENTRY_TYPE_DONATION,
    PAYMENT_FAILED,
    PAYMENT_REFUNDED,
    PAYMENT_SUCCEEDED,
)
from apps.finance.infrastructure.payment_adapters import parse_webhook_payload
from apps.finance.models import LedgerEntry, PaymentTransaction, PaymentWebhookEvent


@transaction.atomic
def process_webhook(*, provider: str, payload: dict) -> tuple[PaymentWebhookEvent, bool]:
    parsed = parse_webhook_payload(provider, payload)
    if not parsed["event_id"]:
        raise ValueError("Webhook payload missing event id")

    webhook_event, created = PaymentWebhookEvent.objects.get_or_create(
        provider=provider,
        event_id=parsed["event_id"],
        defaults={
            "event_type": parsed["event_type"],
            "payload": payload,
        },
    )
    if not created:
        return webhook_event, False

    tx, _ = PaymentTransaction.objects.get_or_create(
        provider=provider,
        external_id=parsed["external_id"] or parsed["event_id"],
        defaults={
            "status": parsed["status"],
            "amount_minor": parsed["amount_minor"],
            "currency": parsed["currency"],
            "payload": payload,
        },
    )

    tx.status = parsed["status"]
    tx.amount_minor = parsed["amount_minor"]
    tx.currency = parsed["currency"]
    tx.payload = payload
    tx.save(update_fields=["status", "amount_minor", "currency", "payload", "updated_at"])

    if parsed["status"] == PAYMENT_SUCCEEDED:
        LedgerEntry.objects.create(
            entry_type=ENTRY_TYPE_DONATION,
            direction=DIRECTION_CREDIT,
            amount_minor=parsed["amount_minor"],
            currency=parsed["currency"],
            description="Payment webhook succeeded",
            reference=tx.external_id,
            metadata={"provider": provider, "event_id": parsed["event_id"]},
        )
    elif parsed["status"] in {PAYMENT_FAILED, PAYMENT_REFUNDED}:
        # Keep audit trail in transaction status; no credit entry written.
        pass

    webhook_event.processed_at = timezone.now()
    webhook_event.save(update_fields=["processed_at"])
    return webhook_event, True


def reconciliation_summary(*, currency: str = "GBP") -> dict:
    totals = (
        LedgerEntry.objects.filter(currency=currency.upper())
        .values("entry_type", "direction")
        .annotate(total_minor=Sum("amount_minor"))
    )

    payments = (
        PaymentTransaction.objects.filter(currency=currency.upper())
        .values("status")
        .annotate(total_minor=Sum("amount_minor"))
    )

    return {
        "currency": currency.upper(),
        "ledger_totals": list(totals),
        "payment_totals": list(payments),
    }
