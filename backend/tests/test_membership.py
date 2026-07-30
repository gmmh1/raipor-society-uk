from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.membership.domain.status import STATUS_ACTIVE, STATUS_CANCELLED, STATUS_PENDING
from apps.membership.models import Membership, MembershipStatusTransition


@pytest.mark.django_db
def test_membership_me_requires_authentication():
    client = APIClient()
    response = client.get(reverse("membership-me"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_membership_me_creates_default_membership():
    user = User.objects.create_user(username="member1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("membership-me"))

    assert response.status_code == 200
    assert response.json()["status"] == STATUS_PENDING
    assert Membership.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_membership_transition_requires_role_permission():
    admin_user = User.objects.create_user(username="admin1", password="pass123")
    target_user = User.objects.create_user(username="target1", password="pass123")
    membership = Membership.objects.create(user=target_user)

    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.post(
        reverse("membership-transition"),
        data={"membership_id": str(membership.id), "to_status": STATUS_ACTIVE},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_membership_transition_updates_status_and_writes_audit():
    admin_user = User.objects.create_user(username="admin2", password="pass123")
    admin_role = Role.objects.create(code="admin", name="Admin")
    admin_user.roles.add(admin_role)

    target_user = User.objects.create_user(username="target2", password="pass123")
    membership = Membership.objects.create(user=target_user)

    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.post(
        reverse("membership-transition"),
        data={
            "membership_id": str(membership.id),
            "to_status": STATUS_ACTIVE,
            "reason": "Approved by committee",
        },
        format="json",
    )

    membership.refresh_from_db()

    assert response.status_code == 200
    assert membership.status == STATUS_ACTIVE
    assert MembershipStatusTransition.objects.filter(
        membership=membership,
        from_status=STATUS_PENDING,
        to_status=STATUS_ACTIVE,
    ).count() == 1


@pytest.mark.django_db
def test_membership_transition_rejects_invalid_transition():
    admin_user = User.objects.create_user(username="admin3", password="pass123")
    admin_role = Role.objects.create(code="admin", name="Admin")
    admin_user.roles.add(admin_role)

    target_user = User.objects.create_user(username="target3", password="pass123")
    membership = Membership.objects.create(user=target_user, status=STATUS_PENDING)

    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.post(
        reverse("membership-transition"),
        data={"membership_id": str(membership.id), "to_status": STATUS_CANCELLED},
        format="json",
    )

    assert response.status_code == 200

    invalid_response = client.post(
        reverse("membership-transition"),
        data={"membership_id": str(membership.id), "to_status": STATUS_PENDING},
        format="json",
    )

    assert invalid_response.status_code == 400


@pytest.mark.django_db
def test_membership_admin_list_requires_role():
    member = User.objects.create_user(username="plain-member", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(reverse("membership-admin-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_membership_admin_list_filters_by_status_and_search():
    admin_user = User.objects.create_user(username="admin-lister", password="pass123")
    admin_role = Role.objects.create(code="admin", name="Admin")
    admin_user.roles.add(admin_role)

    active_user = User.objects.create_user(
        username="alice-active", email="alice@example.com", password="pass123"
    )
    Membership.objects.create(user=active_user, status=STATUS_ACTIVE)

    pending_user = User.objects.create_user(username="bob-pending", password="pass123")
    Membership.objects.create(user=pending_user, status=STATUS_PENDING)

    client = APIClient()
    client.force_authenticate(user=admin_user)

    status_response = client.get(reverse("membership-admin-list"), {"status": STATUS_ACTIVE})
    assert status_response.status_code == 200
    status_results = status_response.json()["results"]
    assert {item["username"] for item in status_results} == {"alice-active"}

    search_response = client.get(reverse("membership-admin-list"), {"q": "alice"})
    search_results = search_response.json()["results"]
    assert {item["username"] for item in search_results} == {"alice-active"}

    unknown_status_response = client.get(
        reverse("membership-admin-list"), {"status": "not-a-real-status"}
    )
    assert unknown_status_response.status_code == 400


@pytest.mark.django_db
def test_backfill_memberships_creates_missing_rows_only():
    has_membership = User.objects.create_user(username="already-has-one", password="pass123")
    Membership.objects.create(user=has_membership, status=STATUS_ACTIVE)

    missing_a = User.objects.create_user(username="missing-membership-a", password="pass123")
    missing_b = User.objects.create_user(username="missing-membership-b", password="pass123")

    out = StringIO()
    call_command("backfill_memberships", stdout=out)

    assert "Created 2 missing membership record(s)." in out.getvalue()
    assert Membership.objects.filter(user=missing_a).exists()
    assert Membership.objects.filter(user=missing_b).exists()
    assert Membership.objects.filter(user=has_membership).count() == 1

    # Idempotent: running it again with nothing missing creates zero more.
    out2 = StringIO()
    call_command("backfill_memberships", stdout=out2)
    assert "Created 0 missing membership record(s)." in out2.getvalue()
