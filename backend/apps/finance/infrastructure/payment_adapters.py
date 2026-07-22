import requests
import stripe
from django.conf import settings

from apps.finance.domain.types import (
    PAYMENT_FAILED,
    PAYMENT_REFUNDED,
    PAYMENT_SUCCEEDED,
    PROVIDER_PAYPAL,
    PROVIDER_STRIPE,
)


class WebhookVerificationError(ValueError):
    pass


def verify_stripe_signature(*, payload_body: bytes, sig_header: str) -> dict:
    """Verify a Stripe webhook using the official SDK. Returns the verified event dict.

    Fails closed: an unset secret outside DEBUG is treated as a configuration error,
    never as "skip verification".
    """
    secret = settings.STRIPE_WEBHOOK_SECRET
    if not secret:
        if settings.DEBUG:
            raise WebhookVerificationError(
                "STRIPE_WEBHOOK_SECRET is not configured; refusing to accept unverified webhook."
            )
        raise RuntimeError("STRIPE_WEBHOOK_SECRET must be set outside DEBUG.")

    try:
        event = stripe.Webhook.construct_event(payload_body, sig_header, secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise WebhookVerificationError(f"Stripe signature verification failed: {exc}") from exc
    return event


def verify_paypal_signature(*, headers: dict, payload_body: bytes, transmission_data: dict) -> bool:
    """Verify a PayPal webhook via PayPal's server-side verify-webhook-signature API.

    ``transmission_data`` must contain: transmission_id, transmission_time, cert_url,
    auth_algo, transmission_sig (all read from the incoming request headers).
    """
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    if not webhook_id:
        if settings.DEBUG:
            raise WebhookVerificationError(
                "PAYPAL_WEBHOOK_ID is not configured; refusing to accept unverified webhook."
            )
        raise RuntimeError("PAYPAL_WEBHOOK_ID must be set outside DEBUG.")

    token = _get_paypal_access_token()
    response = requests.post(
        f"{settings.PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "transmission_id": transmission_data.get("transmission_id"),
            "transmission_time": transmission_data.get("transmission_time"),
            "cert_url": transmission_data.get("cert_url"),
            "auth_algo": transmission_data.get("auth_algo"),
            "transmission_sig": transmission_data.get("transmission_sig"),
            "webhook_id": webhook_id,
            "webhook_event": payload_body,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("verification_status") == "SUCCESS"


def _get_paypal_access_token() -> str:
    response = requests.post(
        f"{settings.PAYPAL_API_BASE}/v1/oauth2/token",
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


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
