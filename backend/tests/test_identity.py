import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User


@pytest.mark.django_db
def test_identity_me_requires_authentication():
    client = APIClient()
    response = client.get(reverse("identity-me"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_identity_me_returns_user_profile_and_roles():
    user = User.objects.create_user(username="alice", password="pass123", email="alice@example.com")
    admin_role = Role.objects.create(code="admin", name="Admin")
    user.roles.add(admin_role)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("identity-me"))
    payload = response.json()

    assert response.status_code == 200
    assert payload["username"] == "alice"
    assert payload["email"] == "alice@example.com"
    assert payload["roles"] == ["admin"]


@pytest.mark.django_db
def test_rbac_check_returns_authorized_true_for_matching_role():
    user = User.objects.create_user(username="bob", password="pass123")
    role = Role.objects.create(code="member", name="Member")
    user.roles.add(role)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("identity-rbac-check"), data={"roles": ["member", "admin"]}, format="json")

    assert response.status_code == 200
    assert response.json()["authorized"] is True
    assert response.json()["matched_roles"] == ["member"]


@pytest.mark.django_db
def test_rbac_check_returns_authorized_false_for_missing_roles():
    user = User.objects.create_user(username="charlie", password="pass123")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse("identity-rbac-check"), data={"roles": ["admin"]}, format="json")

    assert response.status_code == 200
    assert response.json()["authorized"] is False
    assert response.json()["matched_roles"] == []
