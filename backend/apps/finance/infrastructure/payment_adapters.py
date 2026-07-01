from apps.finance.domain.types import (
    PAYMENT_FAILED,
    PAYMENT_REFUNDED,
    PAYMENT_SUCCEEDED,
    PROVIDER_PAYPAL,
    PROVIDER_STRIPE,
)


def parse_webhook_payload(provider: str, payload: dict) -> dict:
    event_id = str(payload.get("id") or payload.get("event_id") or "")
    event_type = str(payload.get("type") or payload.get("event_type") or "")

    amount_minor = 0
    currency = "GBP"
    external_id = ""
    status = PAYMENT_FAILED

    if provider == PROVIDER_STRIPE:
        data_obj = payload.get("data", {}).get("object", {})
        amount_minor = int(data_obj.get("amount_total") or data_obj.get("amount") or 0)
        currency = str(data_obj.get("currency") or "gbp").upper()
        external_id = str(data_obj.get("id") or event_id)
        stripe_status = str(data_obj.get("status") or "")
        if stripe_status in {"succeeded", "paid", "complete"}:
            status = PAYMENT_SUCCEEDED
        elif stripe_status in {"refunded"}:
            status = PAYMENT_REFUNDED
        else:
            status = PAYMENT_FAILED

    elif provider == PROVIDER_PAYPAL:
        resource = payload.get("resource", {})
        amount = resource.get("amount", {})
        value = amount.get("value") or resource.get("amount", {}).get("value") or "0"
        amount_minor = int(round(float(value) * 100))
        currency = str(amount.get("currency_code") or "GBP").upper()
        external_id = str(resource.get("id") or event_id)
        pp_status = str(resource.get("status") or payload.get("event_type") or "")
        if "COMPLETED" in pp_status.upper() or "SUCCEEDED" in pp_status.upper():
            status = PAYMENT_SUCCEEDED
        elif "REFUND" in pp_status.upper():
            status = PAYMENT_REFUNDED
        else:
            status = PAYMENT_FAILED

    return {
        "event_id": event_id,
        "event_type": event_type,
        "external_id": external_id,
        "amount_minor": amount_minor,
        "currency": currency,
        "status": status,
    }
