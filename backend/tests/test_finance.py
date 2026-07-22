import hmac
import json
import time
from hashlib import sha256

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.finance.models import LedgerEntry, PaymentTransaction, PaymentWebhookEvent
from apps.identity.models import Role, User

STRIPE_TEST_SECRET = "whsec_test_secret"


def _stripe_signature_header(payload_body: bytes, secret: str, timestamp: int | None = None) -> str:
    ts = timestamp if timestamp is not None else int(time.time())
    signed_payload = f"{ts}.{payload_body.decode()}".encode()
    signature = hmac.new(secret.encode(), signed_payload, sha256).hexdigest()
    return f"t={ts},v1={signature}"


def _stripe_event_body(event_id: str = "evt_1") -> bytes:
    payload = {
        "id": event_id,
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_1",
                "amount_total": 5000,
                "currency": "gbp",
                "status": "complete",
            }
        },
    }
    return json.dumps(payload).encode()


@pytest.mark.django_db
def test_ledger_create_requires_treasurer_or_admin():
    user = User.objects.create_user(username="finance-user-1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("finance-ledger-entry-create"),
        data={
            "entry_type": "donation",
            "direction": "credit",
            "amount_minor": 1000,
            "currency": "GBP",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_ledger_create_success_with_treasurer_role():
    user = User.objects.create_user(username="finance-user-2", password="pass123")
    role = Role.objects.create(code="treasurer", name="Treasurer")
    user.roles.add(role)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("finance-ledger-entry-create"),
        data={
            "entry_type": "donation",
            "direction": "credit",
            "amount_minor": 2500,
            "currency": "GBP",
            "description": "Donation intake",
            "reference": "DON-001",
        },
        format="json",
    )

    assert response.status_code == 201
    assert LedgerEntry.objects.count() == 1


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=STRIPE_TEST_SECRET)
def test_stripe_webhook_idempotency_by_provider_event_id():
    client = APIClient()
    body = _stripe_event_body("evt_1")
    header = _stripe_signature_header(body, STRIPE_TEST_SECRET)

    first = client.post(
        reverse("finance-webhook-stripe"),
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=header,
    )
    second = client.post(
        reverse("finance-webhook-stripe"),
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=header,
    )

    assert first.status_code == 200
    assert first.json()["processed_now"] is True
    assert second.status_code == 200
    assert second.json()["processed_now"] is False
    assert PaymentTransaction.objects.count() == 1


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=STRIPE_TEST_SECRET)
def test_stripe_webhook_rejects_invalid_signature():
    client = APIClient()
    body = _stripe_event_body("evt_forged")

    response = client.post(
        reverse("finance-webhook-stripe"),
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="t=1,v1=not-a-real-signature",
    )

    assert response.status_code == 400
    assert PaymentWebhookEvent.objects.count() == 0
    assert LedgerEntry.objects.count() == 0


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=STRIPE_TEST_SECRET)
def test_stripe_webhook_rejects_missing_signature_header():
    client = APIClient()
    body = _stripe_event_body("evt_no_header")

    response = client.post(
        reverse("finance-webhook-stripe"),
        data=body,
        content_type="application/json",
    )

    assert response.status_code == 400
    assert PaymentWebhookEvent.objects.count() == 0


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET="", DEBUG=False)
def test_stripe_webhook_fails_closed_when_secret_unset_outside_debug():
    client = APIClient()
    body = _stripe_event_body("evt_no_secret")
    header = _stripe_signature_header(body, "irrelevant-secret")

    with pytest.raises(RuntimeError):
        client.post(
            reverse("finance-webhook-stripe"),
            data=body,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=header,
        )

    assert PaymentWebhookEvent.objects.count() == 0


@pytest.mark.django_db
@override_settings(PAYPAL_WEBHOOK_ID="test-webhook-id")
def test_paypal_webhook_accepts_verified_payload(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.presentation.views.verify_paypal_signature",
        lambda **kwargs: True,
    )

    client = APIClient()
    body = json.dumps(
        {
            "id": "WH-1",
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAP-1",
                "status": "COMPLETED",
                "amount": {"value": "12.50", "currency_code": "GBP"},
            },
        }
    ).encode()

    response = client.post(
        reverse("finance-webhook-paypal"),
        data=body,
        content_type="application/json",
        HTTP_PAYPAL_TRANSMISSION_ID="txn-1",
        HTTP_PAYPAL_TRANSMISSION_TIME="2026-01-01T00:00:00Z",
        HTTP_PAYPAL_CERT_URL="https://api.paypal.com/cert",
        HTTP_PAYPAL_AUTH_ALGO="SHA256withRSA",
        HTTP_PAYPAL_TRANSMISSION_SIG="sig",
    )

    assert response.status_code == 200
    assert response.json()["processed_now"] is True
    assert PaymentTransaction.objects.count() == 1


@pytest.mark.django_db
@override_settings(PAYPAL_WEBHOOK_ID="test-webhook-id")
def test_paypal_webhook_rejects_unverified_payload(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.presentation.views.verify_paypal_signature",
        lambda **kwargs: False,
    )

    client = APIClient()
    body = json.dumps(
        {
            "id": "WH-2",
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAP-2",
                "status": "COMPLETED",
                "amount": {"value": "5.00", "currency_code": "GBP"},
            },
        }
    ).encode()

    response = client.post(
        reverse("finance-webhook-paypal"),
        data=body,
        content_type="application/json",
        HTTP_PAYPAL_TRANSMISSION_ID="txn-2",
        HTTP_PAYPAL_TRANSMISSION_TIME="2026-01-01T00:00:00Z",
        HTTP_PAYPAL_CERT_URL="https://api.paypal.com/cert",
        HTTP_PAYPAL_AUTH_ALGO="SHA256withRSA",
        HTTP_PAYPAL_TRANSMISSION_SIG="bad-sig",
    )

    assert response.status_code == 400
    assert PaymentWebhookEvent.objects.count() == 0


@pytest.mark.django_db
def test_reconciliation_summary_requires_role_and_returns_data():
    user = User.objects.create_user(username="finance-user-3", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    forbidden = client.get(reverse("finance-reconciliation-summary"))
    assert forbidden.status_code == 403

    role = Role.objects.create(code="admin", name="Admin")
    user.roles.add(role)

    LedgerEntry.objects.create(
        entry_type="donation",
        direction="credit",
        amount_minor=3000,
        currency="GBP",
        reference="DON-002",
    )

    allowed = client.get(reverse("finance-reconciliation-summary"))
    assert allowed.status_code == 200
    assert allowed.json()["currency"] == "GBP"
    assert isinstance(allowed.json()["ledger_totals"], list)
    assert isinstance(allowed.json()["payment_totals"], list)
