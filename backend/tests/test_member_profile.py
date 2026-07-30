import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.membership.models import MemberProfile


@pytest.mark.django_db
def test_my_profile_get_creates_default_profile():
    user = User.objects.create_user(username="profile-user-1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("membership-profile-me"))

    assert response.status_code == 200
    assert response.json()["public_consent"] is False
    assert MemberProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_my_profile_update_sets_own_fields_and_phone():
    user = User.objects.create_user(username="profile-user-2", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("membership-profile-me"),
        data={
            "avatar_url": "https://example.com/me.jpg",
            "bio": "Hello there.",
            "public_consent": True,
            "phone_number": "+441234567890",
        },
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["avatar_url"] == "https://example.com/me.jpg"
    assert body["bio"] == "Hello there."
    assert body["public_consent"] is True
    assert body["phone_number"] == "+441234567890"

    user.refresh_from_db()
    assert user.phone_number == "+441234567890"


@pytest.mark.django_db
def test_my_profile_update_cannot_set_position():
    """Position isn't in ProfileUpdateRequestSerializer at all — a member posting
    a position field must have no effect, since it's admin-only (see set_position)."""
    user = User.objects.create_user(username="profile-user-3", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("membership-profile-me"),
        data={"position": "Chair", "public_consent": True},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["position"] == ""


@pytest.mark.django_db
def test_admin_set_position_requires_admin_role():
    target = User.objects.create_user(username="profile-target-1", password="pass123")
    non_admin = User.objects.create_user(username="profile-nonadmin-1", password="pass123")
    Role.objects.create(code="volunteer", name="Volunteer").users.add(non_admin)

    client = APIClient()
    client.force_authenticate(user=non_admin)

    response = client.post(
        reverse("membership-profile-position"),
        data={"user_id": str(target.id), "position": "Secretary"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_set_position_updates_profile():
    target = User.objects.create_user(username="profile-target-2", password="pass123")
    admin = User.objects.create_user(username="profile-admin-1", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        reverse("membership-profile-position"),
        data={"user_id": str(target.id), "position": "Treasurer", "display_order": 2},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["position"] == "Treasurer"
    profile = MemberProfile.objects.get(user=target)
    assert profile.position == "Treasurer"
    assert profile.display_order == 2


@pytest.mark.django_db
def test_public_roster_splits_committee_and_members_and_respects_consent():
    committee_member = User.objects.create_user(
        username="roster-committee-1", email="chair@example.com", password="pass123"
    )
    MemberProfile.objects.create(
        user=committee_member, position="Chair", public_consent=True, display_order=0
    )

    plain_member = User.objects.create_user(
        username="roster-member-1", email="member@example.com", password="pass123"
    )
    MemberProfile.objects.create(user=plain_member, public_consent=True)

    non_consenting = User.objects.create_user(username="roster-hidden-1", password="pass123")
    MemberProfile.objects.create(user=non_consenting, position="Secretary", public_consent=False)

    client = APIClient()
    response = client.get(reverse("membership-profile-public"))

    assert response.status_code == 200
    body = response.json()
    committee_names = {item["position"] for item in body["committee"]}
    assert committee_names == {"Chair"}
    assert len(body["members"]) == 1
    assert len(body["committee"]) == 1
