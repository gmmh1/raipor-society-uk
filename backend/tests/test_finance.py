import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.finance.models import LedgerEntry, PaymentTransaction
from apps.identity.models import Role, User


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
def test_webhook_idempotency_by_provider_event_id():
    client = APIClient()

    payload = {
        "id": "evt_1",
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

    first = client.post(
        reverse("finance-payment-webhook-ingest"),
        data={"provider": "stripe", "payload": payload},
        format="json",
    )
    second = client.post(
        reverse("finance-payment-webhook-ingest"),
        data={"provider": "stripe", "payload": payload},
        format="json",
    )

    assert first.status_code == 200
    assert first.json()["processed_now"] is True
    assert second.status_code == 200
    assert second.json()["processed_now"] is False
    assert PaymentTransaction.objects.count() == 1


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
