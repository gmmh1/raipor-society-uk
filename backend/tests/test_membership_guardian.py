from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.finance.domain.types import ENTRY_TYPE_MEMBERSHIP_FEE
from apps.finance.models import LedgerEntry
from apps.identity.models import Role, User
from apps.membership.application.lifecycle_service import (
    MembershipLifecycleError,
    transition_membership_status,
)
from apps.membership.application.tier_service import assign_tier, record_dues_payment
from apps.membership.domain.status import STATUS_ACTIVE, STATUS_EXPIRED
from apps.membership.models import GuardianRelationship, Membership, MembershipTier
from apps.membership.tasks import expire_memberships_task


def _minor_dob() -> date:
    return timezone.localdate() - timedelta(days=365 * 10)


def _adult_dob() -> date:
    return timezone.localdate() - timedelta(days=365 * 40)


@pytest.mark.django_db
def test_minor_cannot_activate_membership_without_guardian_consent():
    child = User.objects.create_user(
        username="child1", password="pass123", date_of_birth=_minor_dob()
    )
    membership = Membership.objects.create(user=child)

    with pytest.raises(MembershipLifecycleError, match="guardian consent"):
        transition_membership_status(membership, STATUS_ACTIVE, actor=None)


@pytest.mark.django_db
def test_adult_can_activate_membership_without_guardian_relationship():
    adult = User.objects.create_user(
        username="adult1", password="pass123", date_of_birth=_adult_dob()
    )
    membership = Membership.objects.create(user=adult)

    updated = transition_membership_status(membership, STATUS_ACTIVE, actor=None)
    assert updated.status == STATUS_ACTIVE


@pytest.mark.django_db
def test_guardian_link_and_consent_flow_unlocks_activation():
    admin = User.objects.create_user(username="admin-gs", password="pass123")
    admin.roles.add(Role.objects.create(code="admin", name="Admin"))

    guardian = User.objects.create_user(username="guardian1", password="pass123")
    child = User.objects.create_user(
        username="child2", password="pass123", date_of_birth=_minor_dob()
    )
    membership = Membership.objects.create(user=child)

    client = APIClient()
    client.force_authenticate(user=admin)
    link_response = client.post(
        reverse("membership-guardians-link"),
        data={
            "guardian_id": str(guardian.id),
            "child_id": str(child.id),
            "relationship_type": "parent",
        },
        format="json",
    )
    assert link_response.status_code == 201
    relationship_id = link_response.json()["id"]

    client.force_authenticate(user=child)
    forbidden = client.post(
        reverse("membership-guardians-consent"),
        data={"relationship_id": relationship_id},
        format="json",
    )
    assert forbidden.status_code == 400

    client.force_authenticate(user=guardian)
    consent_response = client.post(
        reverse("membership-guardians-consent"),
        data={"relationship_id": relationship_id},
        format="json",
    )
    assert consent_response.status_code == 200
    assert consent_response.json()["consent_given_at"] is not None

    updated = transition_membership_status(membership, STATUS_ACTIVE, actor=admin)
    assert updated.status == STATUS_ACTIVE


@pytest.mark.django_db
def test_my_guardian_relationships_visible_to_both_sides():
    guardian = User.objects.create_user(username="guardian2", password="pass123")
    child = User.objects.create_user(
        username="child3", password="pass123", date_of_birth=_minor_dob()
    )
    relationship = GuardianRelationship.objects.create(
        guardian=guardian, child=child, relationship_type="parent"
    )

    client = APIClient()

    client.force_authenticate(user=guardian)
    as_guardian = client.get(reverse("membership-guardians-me"))
    assert len(as_guardian.json()) == 1
    assert as_guardian.json()[0]["id"] == str(relationship.id)

    client.force_authenticate(user=child)
    as_child = client.get(reverse("membership-guardians-me"))
    assert len(as_child.json()) == 1


@pytest.mark.django_db
def test_duplicate_guardian_link_rejected():
    admin = User.objects.create_user(username="admin-gs2", password="pass123")
    admin.roles.add(Role.objects.create(code="admin", name="Admin"))
    guardian = User.objects.create_user(username="guardian3", password="pass123")
    child = User.objects.create_user(username="child4", password="pass123")

    GuardianRelationship.objects.create(guardian=guardian, child=child, relationship_type="parent")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(
        reverse("membership-guardians-link"),
        data={
            "guardian_id": str(guardian.id),
            "child_id": str(child.id),
            "relationship_type": "parent",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_assign_tier_and_record_dues_creates_ledger_entry_and_extends_expiry():
    admin = User.objects.create_user(username="admin-tier", password="pass123")
    user = User.objects.create_user(username="dues-user", password="pass123")
    membership = Membership.objects.create(user=user)
    tier = MembershipTier.objects.create(
        code="standard", name="Standard", price_minor=2500, currency="GBP", billing_period_days=365
    )

    assign_tier(membership=membership, tier=tier)
    membership.refresh_from_db()
    assert membership.tier_id == tier.id

    updated = record_dues_payment(membership=membership, actor=admin)
    assert updated.expires_at is not None
    assert updated.expires_at > timezone.now()

    entry = LedgerEntry.objects.get(entry_type=ENTRY_TYPE_MEMBERSHIP_FEE)
    assert entry.amount_minor == 2500
    assert entry.currency == "GBP"


@pytest.mark.django_db
def test_expire_memberships_task_transitions_past_due_active_memberships():
    user = User.objects.create_user(username="expiring-user", password="pass123")
    membership = Membership.objects.create(
        user=user,
        status=STATUS_ACTIVE,
        started_at=timezone.now() - timedelta(days=400),
        expires_at=timezone.now() - timedelta(days=1),
    )

    still_active_user = User.objects.create_user(username="still-active-user", password="pass123")
    Membership.objects.create(
        user=still_active_user,
        status=STATUS_ACTIVE,
        expires_at=timezone.now() + timedelta(days=30),
    )

    count = expire_memberships_task()

    membership.refresh_from_db()
    assert count == 1
    assert membership.status == STATUS_EXPIRED
