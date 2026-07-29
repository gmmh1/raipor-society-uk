from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.finance.domain.types import (
    DIRECTION_CREDIT,
    ENTRY_TYPE_CHOICES,
    ENTRY_TYPE_DONATION,
    ENTRY_TYPE_MEMBERSHIP_FEE,
    ENTRY_TYPE_SHOP_SALE,
    PAYMENT_FAILED,
    PAYMENT_PENDING,
    PAYMENT_REFUNDED,
    PAYMENT_SUCCEEDED,
    PROVIDER_PAYPAL,
    PROVIDER_STRIPE,
)
from apps.finance.infrastructure.payment_adapters import (
    create_paypal_order,
    create_stripe_checkout_session,
    parse_webhook_payload,
)
from apps.finance.models import LedgerEntry, PaymentTransaction, PaymentWebhookEvent


class CheckoutError(ValueError):
    pass


_CHECKOUT_PROVIDERS = {PROVIDER_STRIPE, PROVIDER_PAYPAL}
_VALID_ENTRY_TYPES = {choice[0] for choice in ENTRY_TYPE_CHOICES}


@transaction.atomic
def create_checkout_session(
    *,
    provider: str,
    amount_minor: int,
    currency: str,
    entry_type: str,
    description: str,
    reference: str,
    payer,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Initiates an outbound payment with the provider and records a pending
    ``PaymentTransaction`` so the existing webhook flow can reconcile against it by
    ``(provider, external_id)`` once the provider confirms payment.
    """
    if provider not in _CHECKOUT_PROVIDERS:
        raise CheckoutError(f"Unsupported provider '{provider}' for checkout.")
    if entry_type not in _VALID_ENTRY_TYPES:
        raise CheckoutError(f"Unknown entry type '{entry_type}'.")
    if amount_minor <= 0:
        raise CheckoutError("amount_minor must be positive.")

    if provider == PROVIDER_STRIPE:
        result = create_stripe_checkout_session(
            amount_minor=amount_minor,
            currency=currency,
            description=description,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    else:  # PROVIDER_PAYPAL
        result = create_paypal_order(
            amount_minor=amount_minor,
            currency=currency,
            description=description,
            success_url=success_url,
            cancel_url=cancel_url,
        )

    PaymentTransaction.objects.create(
        provider=provider,
        external_id=result["external_id"],
        status=PAYMENT_PENDING,
        amount_minor=amount_minor,
        currency=currency.upper(),
        payer=payer if getattr(payer, "is_authenticated", False) else None,
        payload={"entry_type": entry_type, "description": description, "reference": reference},
    )

    return {
        "provider": provider,
        "external_id": result["external_id"],
        "redirect_url": result["redirect_url"],
    }


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

    # Capture before ``tx.payload`` is overwritten below with the raw webhook body:
    # if this transaction originated from ``create_checkout_session``, its payload
    # holds the ``entry_type`` the payer actually selected (donation/dues/shop sale)
    # and the ``reference`` the initiating module (e.g. a shop order) needs back.
    checkout_payload = tx.payload if isinstance(tx.payload, dict) else {}
    checkout_entry_type = checkout_payload.get("entry_type")
    checkout_reference = checkout_payload.get("reference")
    ledger_entry_type = (
        checkout_entry_type if checkout_entry_type in _VALID_ENTRY_TYPES else ENTRY_TYPE_DONATION
    )

    tx.status = parsed["status"]
    tx.amount_minor = parsed["amount_minor"]
    tx.currency = parsed["currency"]
    tx.payload = payload
    tx.save(update_fields=["status", "amount_minor", "currency", "payload", "updated_at"])

    if parsed["status"] == PAYMENT_SUCCEEDED:
        LedgerEntry.objects.create(
            entry_type=ledger_entry_type,
            direction=DIRECTION_CREDIT,
            amount_minor=parsed["amount_minor"],
            currency=parsed["currency"],
            description="Payment webhook succeeded",
            reference=tx.external_id,
            metadata={"provider": provider, "event_id": parsed["event_id"]},
        )
        if ledger_entry_type == ENTRY_TYPE_SHOP_SALE and checkout_reference:
            from apps.shop.application.order_service import mark_order_paid_by_reference

            mark_order_paid_by_reference(payment_reference=checkout_reference)
        elif ledger_entry_type == ENTRY_TYPE_MEMBERSHIP_FEE and checkout_reference:
            from apps.membership.application.tier_service import (
                extend_membership_from_payment,
            )

            extend_membership_from_payment(membership_id=checkout_reference)
    elif parsed["status"] in {PAYMENT_FAILED, PAYMENT_REFUNDED}:
        # Keep audit trail in transaction status; no credit entry written.
        pass

    webhook_event.processed_at = timezone.now()
    webhook_event.save(update_fields=["processed_at"])
    return webhook_event, True


PAYMENT_DERIVED_ENTRY_TYPES = (
    ENTRY_TYPE_DONATION,
    ENTRY_TYPE_MEMBERSHIP_FEE,
    ENTRY_TYPE_SHOP_SALE,
)


def reconciliation_summary(*, currency: str = "GBP") -> dict:
    """Ledger/payment totals, plus a variance check between the two.

    The variance compares ledger credits for payment-derived entry types against
    succeeded ``PaymentTransaction`` totals. A non-zero variance means a webhook
    succeeded without a matching ledger entry (or vice versa — e.g. a manual ledger
    entry posted without a real payment) and needs investigation; it does not by
    itself say which side is wrong.
    """
    currency = currency.upper()
    totals = (
        LedgerEntry.objects.filter(currency=currency)
        .values("entry_type", "direction")
        .annotate(total_minor=Sum("amount_minor"))
    )

    payments = (
        PaymentTransaction.objects.filter(currency=currency)
        .values("status")
        .annotate(total_minor=Sum("amount_minor"))
    )

    payment_derived_credit_minor = (
        LedgerEntry.objects.filter(
            currency=currency,
            direction=DIRECTION_CREDIT,
            entry_type__in=PAYMENT_DERIVED_ENTRY_TYPES,
        ).aggregate(total=Sum("amount_minor"))["total"]
        or 0
    )
    succeeded_payments_minor = (
        PaymentTransaction.objects.filter(
            currency=currency, status=PAYMENT_SUCCEEDED
        ).aggregate(total=Sum("amount_minor"))["total"]
        or 0
    )
    variance_minor = payment_derived_credit_minor - succeeded_payments_minor

    return {
        "currency": currency,
        "ledger_totals": list(totals),
        "payment_totals": list(payments),
        "payment_derived_ledger_credit_minor": payment_derived_credit_minor,
        "succeeded_payment_transactions_minor": succeeded_payments_minor,
        "variance_minor": variance_minor,
        "variance_flagged": variance_minor != 0,
    }
