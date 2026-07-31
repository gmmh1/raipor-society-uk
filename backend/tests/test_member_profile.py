import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import User
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
    a position field must have no effect. Position isn't even a MemberProfile
    attribute any more (see Committee/CommitteeMembership in test_committee.py) —
    it's derived per-request from the current committee, admin-assigned only."""
    user = User.objects.create_user(username="profile-user-3", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("membership-profile-me"),
        data={"position": "President", "public_consent": True},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["position"] == ""
