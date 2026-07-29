import hmac
import json
import time
from hashlib import sha256

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.finance.application.payment_service import CheckoutError, create_checkout_session
from apps.finance.application.receipt_service import ReceiptError, issue_receipt
from apps.finance.models import LedgerEntry, PaymentTransaction, PaymentWebhookEvent, Receipt
from apps.finance.tasks import check_reconciliation_variance_task
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


@pytest.mark.django_db
def test_reconciliation_summary_flags_variance_when_ledger_and_payments_disagree():
    LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=3000, currency="GBP"
    )
    PaymentTransaction.objects.create(
        provider="stripe", external_id="cs_variance", status="succeeded", amount_minor=1000,
        currency="GBP",
    )

    role = Role.objects.create(code="treasurer", name="Treasurer")
    user = User.objects.create_user(username="finance-user-variance", password="pass123")
    user.roles.add(role)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("finance-reconciliation-summary"))
    data = response.json()

    assert data["payment_derived_ledger_credit_minor"] == 3000
    assert data["succeeded_payment_transactions_minor"] == 1000
    assert data["variance_minor"] == 2000
    assert data["variance_flagged"] is True


@pytest.mark.django_db
def test_create_checkout_session_stripe_records_pending_transaction(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.application.payment_service.create_stripe_checkout_session",
        lambda **kwargs: {"external_id": "cs_new_1", "redirect_url": "https://stripe.example/pay"},
    )

    payer = User.objects.create_user(username="checkout-user-1", password="pass123")
    result = create_checkout_session(
        provider="stripe",
        amount_minor=5000,
        currency="GBP",
        entry_type="membership_fee",
        description="Annual dues",
        reference="DUES-1",
        payer=payer,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )

    assert result["redirect_url"] == "https://stripe.example/pay"
    tx = PaymentTransaction.objects.get(external_id="cs_new_1")
    assert tx.status == "pending"
    assert tx.payer == payer
    assert tx.payload["entry_type"] == "membership_fee"


@pytest.mark.django_db
def test_create_checkout_session_rejects_manual_provider():
    payer = User.objects.create_user(username="checkout-user-2", password="pass123")
    with pytest.raises(CheckoutError):
        create_checkout_session(
            provider="manual",
            amount_minor=1000,
            currency="GBP",
            entry_type="donation",
            description="",
            reference="",
            payer=payer,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )


@pytest.mark.django_db
def test_checkout_endpoint_requires_authentication_for_non_donation_entry_types():
    client = APIClient()
    response = client.post(
        reverse("finance-payments-checkout"),
        data={
            "provider": "stripe",
            "entry_type": "membership_fee",
            "amount_minor": 1000,
            "success_url": "https://example.com/s",
            "cancel_url": "https://example.com/c",
        },
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_checkout_endpoint_allows_anonymous_donations(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.application.payment_service.create_stripe_checkout_session",
        lambda **kwargs: {"external_id": "cs_anon_1", "redirect_url": "https://stripe.example/checkout"},
    )

    client = APIClient()
    response = client.post(
        reverse("finance-payments-checkout"),
        data={
            "provider": "stripe",
            "entry_type": "donation",
            "amount_minor": 1000,
            "success_url": "https://example.com/s",
            "cancel_url": "https://example.com/c",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["redirect_url"] == "https://stripe.example/checkout"


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=STRIPE_TEST_SECRET)
def test_webhook_uses_entry_type_recorded_at_checkout():
    payer = User.objects.create_user(username="checkout-user-3", password="pass123")
    PaymentTransaction.objects.create(
        provider="stripe",
        external_id="cs_test_1",
        status="pending",
        amount_minor=5000,
        currency="GBP",
        payer=payer,
        payload={"entry_type": "membership_fee", "description": "Dues", "reference": "DUES-2"},
    )

    client = APIClient()
    body = _stripe_event_body("evt_membership_1")
    header = _stripe_signature_header(body, STRIPE_TEST_SECRET)

    response = client.post(
        reverse("finance-webhook-stripe"),
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=header,
    )

    assert response.status_code == 200
    entry = LedgerEntry.objects.get(reference="cs_test_1")
    assert entry.entry_type == "membership_fee"


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=STRIPE_TEST_SECRET)
def test_webhook_membership_fee_payment_extends_membership_expiry():
    from apps.membership.domain.status import STATUS_ACTIVE
    from apps.membership.models import Membership, MembershipTier

    payer = User.objects.create_user(username="checkout-user-4", password="pass123")
    tier = MembershipTier.objects.create(
        code="standard", name="Standard", price_minor=5000, billing_period_days=365
    )
    membership = Membership.objects.create(user=payer, status=STATUS_ACTIVE, tier=tier)
    assert membership.expires_at is None

    PaymentTransaction.objects.create(
        provider="stripe",
        external_id="cs_test_1",
        status="pending",
        amount_minor=5000,
        currency="GBP",
        payer=payer,
        payload={
            "entry_type": "membership_fee",
            "description": "Dues",
            "reference": str(membership.id),
        },
    )

    client = APIClient()
    body = _stripe_event_body("evt_membership_2")
    header = _stripe_signature_header(body, STRIPE_TEST_SECRET)
    response = client.post(
        reverse("finance-webhook-stripe"),
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=header,
    )

    assert response.status_code == 200
    membership.refresh_from_db()
    assert membership.expires_at is not None


@pytest.mark.django_db
def test_issue_receipt_generates_pdf_and_uploads_to_storage(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "apps.finance.application.receipt_service.render_receipt_pdf",
        lambda context: b"%PDF-1.4 fake",
    )
    monkeypatch.setattr(
        "apps.finance.application.receipt_service.storage.upload_bytes",
        lambda **kwargs: captured.update(kwargs),
    )

    recipient = User.objects.create_user(username="receipt-user-1", password="pass123")
    admin = User.objects.create_user(username="receipt-admin-1", password="pass123")
    ledger_entry = LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=4500, currency="GBP",
        description="Generous donation",
    )

    receipt = issue_receipt(ledger_entry=ledger_entry, recipient=recipient, actor=admin)

    assert receipt.receipt_number.startswith("RCT-")
    assert receipt.pdf_file_key == captured["key"]
    assert captured["content_type"] == "application/pdf"
    assert Receipt.objects.filter(ledger_entry=ledger_entry).count() == 1


@pytest.mark.django_db
def test_issue_receipt_rejects_duplicate_for_same_ledger_entry(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.application.receipt_service.render_receipt_pdf", lambda context: b"pdf"
    )
    monkeypatch.setattr(
        "apps.finance.application.receipt_service.storage.upload_bytes", lambda **kwargs: None
    )

    admin = User.objects.create_user(username="receipt-admin-2", password="pass123")
    ledger_entry = LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=1000, currency="GBP"
    )
    issue_receipt(ledger_entry=ledger_entry, recipient=None, actor=admin)

    with pytest.raises(ReceiptError):
        issue_receipt(ledger_entry=ledger_entry, recipient=None, actor=admin)


@pytest.mark.django_db
def test_receipt_download_requires_owner_or_role(monkeypatch):
    monkeypatch.setattr(
        "apps.finance.application.receipt_service.storage.generate_presigned_download_url",
        lambda **kwargs: "https://minio.example/receipts/RCT-1.pdf",
    )

    owner = User.objects.create_user(username="receipt-owner-1", password="pass123")
    stranger = User.objects.create_user(username="receipt-stranger-1", password="pass123")
    ledger_entry = LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=1000, currency="GBP"
    )
    receipt = Receipt.objects.create(
        ledger_entry=ledger_entry,
        recipient=owner,
        receipt_number="RCT-TEST-1",
        amount_minor=1000,
        currency="GBP",
        pdf_file_key="receipts/RCT-TEST-1.pdf",
    )

    stranger_client = APIClient()
    stranger_client.force_authenticate(user=stranger)
    forbidden = stranger_client.get(
        reverse("finance-receipts-download", kwargs={"receipt_id": receipt.id})
    )
    assert forbidden.status_code == 403

    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    allowed = owner_client.get(
        reverse("finance-receipts-download", kwargs={"receipt_id": receipt.id})
    )
    assert allowed.status_code == 200
    assert allowed.json()["url"] == "https://minio.example/receipts/RCT-1.pdf"


@pytest.mark.django_db
def test_my_receipts_lists_only_own_receipts():
    owner = User.objects.create_user(username="receipt-owner-2", password="pass123")
    stranger = User.objects.create_user(username="receipt-stranger-2", password="pass123")
    ledger_entry = LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=2000, currency="GBP"
    )
    other_ledger_entry = LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=3000, currency="GBP"
    )
    Receipt.objects.create(
        ledger_entry=ledger_entry,
        recipient=owner,
        receipt_number="RCT-TEST-2",
        amount_minor=2000,
        currency="GBP",
        pdf_file_key="receipts/RCT-TEST-2.pdf",
    )
    Receipt.objects.create(
        ledger_entry=other_ledger_entry,
        recipient=stranger,
        receipt_number="RCT-TEST-3",
        amount_minor=3000,
        currency="GBP",
        pdf_file_key="receipts/RCT-TEST-3.pdf",
    )

    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    response = owner_client.get(reverse("finance-receipts-me"))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["receipt_number"] == "RCT-TEST-2"


@pytest.mark.django_db
def test_check_reconciliation_variance_task_notifies_admins_when_flagged(monkeypatch):
    monkeypatch.setattr(
        "apps.notifications.application.notification_orchestrator.dispatch_notification_task.delay",
        lambda _notification_id: None,
    )

    LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=3000, currency="GBP"
    )
    role = Role.objects.create(code="treasurer", name="Treasurer")
    treasurer = User.objects.create_user(username="variance-treasurer-1", password="pass123")
    treasurer.roles.add(role)

    notified = check_reconciliation_variance_task()

    assert notified == 1
    from apps.notifications.models import Notification

    assert Notification.objects.filter(recipient=treasurer, channel="email").exists()


@pytest.mark.django_db
def test_check_reconciliation_variance_task_silent_when_balanced():
    PaymentTransaction.objects.create(
        provider="stripe", external_id="cs_balanced_1", status="succeeded", amount_minor=2000,
        currency="GBP",
    )
    LedgerEntry.objects.create(
        entry_type="donation", direction="credit", amount_minor=2000, currency="GBP"
    )
    role = Role.objects.create(code="admin", name="Admin")
    admin = User.objects.create_user(username="variance-admin-1", password="pass123")
    admin.roles.add(role)

    notified = check_reconciliation_variance_task()

    assert notified == 0
