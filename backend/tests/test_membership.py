import pytest
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
