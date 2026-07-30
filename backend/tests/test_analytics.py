from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.analytics.application.reports import (
    chat_report,
    events_report,
    finance_report,
    membership_report,
    shop_report,
    voting_report,
)
from apps.chat.application.channel_service import create_direct_channel, post_message
from apps.events.models import Event
from apps.finance.domain.types import DIRECTION_CREDIT, ENTRY_TYPE_DONATION
from apps.finance.models import LedgerEntry
from apps.identity.models import Role, User
from apps.membership.domain.status import STATUS_ACTIVE
from apps.membership.models import Membership
from apps.shop.models import Product, ShopOrder
from apps.voting.application.poll_service import create_poll


def _make_admin(username: str) -> User:
    user = User.objects.create_user(username=username, password="pass123")
    role, _ = Role.objects.get_or_create(code="admin", defaults={"name": "Admin"})
    user.roles.add(role)
    return user


@pytest.mark.django_db
def test_membership_report_counts_by_status():
    active_user = User.objects.create_user(username="member-active", password="pass123")
    pending_user = User.objects.create_user(username="member-pending", password="pass123")
    Membership.objects.create(user=active_user, status=STATUS_ACTIVE)
    Membership.objects.create(user=pending_user)

    report = membership_report()

    assert report["total"] == 2
    assert report["by_status"]["active"] == 1
    assert report["by_status"]["pending"] == 1


@pytest.mark.django_db
def test_events_report_counts_upcoming_and_registrations():
    now = timezone.now()
    Event.objects.create(
        title="Upcoming Gala",
        starts_at=now + timedelta(days=5),
        ends_at=now + timedelta(days=5, hours=2),
        capacity=100,
        is_published=True,
    )
    past_start = now - timedelta(days=5)
    Event.objects.create(
        title="Past Meetup",
        starts_at=past_start,
        ends_at=past_start + timedelta(hours=2),
        capacity=50,
        is_published=True,
    )

    report = events_report()

    assert report["total_events"] == 2
    assert report["upcoming_events"] == 1


@pytest.mark.django_db
def test_finance_report_sums_credit_entries():
    LedgerEntry.objects.create(
        entry_type=ENTRY_TYPE_DONATION,
        direction=DIRECTION_CREDIT,
        amount_minor=5000,
        currency="GBP",
    )
    LedgerEntry.objects.create(
        entry_type=ENTRY_TYPE_DONATION,
        direction=DIRECTION_CREDIT,
        amount_minor=2500,
        currency="GBP",
    )

    report = finance_report(currency="GBP")

    assert report["total_credit_minor"] == 7500
    assert report["credit_last_30_days_minor"] == 7500
    assert "reconciliation_variance_flagged" in report


@pytest.mark.django_db
def test_shop_report_computes_revenue_from_paid_and_fulfilled_orders():
    customer = User.objects.create_user(username="shop-analytics-1", password="pass123")
    Product.objects.create(
        name="Item", sku="SKU-ANALYTICS", price_minor=1000, inventory_count=5, is_active=True
    )
    ShopOrder.objects.create(user=customer, status="paid", total_minor=1000, currency="GBP")
    ShopOrder.objects.create(user=customer, status="pending", total_minor=500, currency="GBP")

    report = shop_report()

    assert report["total_orders"] == 2
    assert report["revenue_minor"] == 1000
    assert report["orders_by_status"]["paid"] == 1
    assert report["orders_by_status"]["pending"] == 1


@pytest.mark.django_db
def test_chat_report_counts_messages_and_flags():
    alice = User.objects.create_user(username="chat-analytics-1", password="pass123")
    bob = User.objects.create_user(username="chat-analytics-2", password="pass123")
    channel = create_direct_channel(initiator=alice, other_user=bob)
    post_message(channel=channel, sender=alice, content="hello")

    report = chat_report()

    assert report["total_channels"] == 1
    assert report["total_messages"] == 1
    assert report["flagged_messages"] == 0


@pytest.mark.django_db
def test_voting_report_counts_open_polls_and_ballots():
    admin = _make_admin("voting-analytics-admin")
    now = timezone.now()
    create_poll(
        title="Open Poll",
        description="",
        options=[{"text": "Yes", "image_url": ""}, {"text": "No", "image_url": ""}],
        opens_at=now - timedelta(hours=1),
        closes_at=now + timedelta(hours=1),
        quorum=0,
        visibility="member",
        creator=admin,
    )
    create_poll(
        title="Closed Poll",
        description="",
        options=[{"text": "Yes", "image_url": ""}, {"text": "No", "image_url": ""}],
        opens_at=now - timedelta(days=2),
        closes_at=now - timedelta(days=1),
        quorum=0,
        visibility="member",
        creator=admin,
    )

    report = voting_report()

    assert report["total_polls"] == 2
    assert report["open_polls"] == 1


@pytest.mark.django_db
def test_analytics_overview_endpoint_requires_staff_role():
    member = User.objects.create_user(username="analytics-member", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(reverse("analytics-overview"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_analytics_overview_endpoint_returns_all_sections():
    admin = _make_admin("analytics-admin-1")
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get(reverse("analytics-overview"))

    assert response.status_code == 200
    body = response.json()
    for section in (
        "membership",
        "events",
        "finance",
        "shop",
        "documents",
        "assistant",
        "chat",
        "voting",
    ):
        assert section in body
