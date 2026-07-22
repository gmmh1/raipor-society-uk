import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from apps.identity.models import EmailVerificationToken, User


@pytest.fixture(autouse=True)
def _reset_throttle_cache():
    # The "auth" scope throttle counter is keyed by client IP and persists in the
    # process-wide cache across tests; reset it so each test starts unthrottled.
    cache.clear()
    yield


@pytest.mark.django_db
def test_register_verify_login_refresh_logout_flow():
    client = APIClient()

    register_response = client.post(
        reverse("identity-register"),
        data={
            "username": "newmember",
            "email": "newmember@example.com",
            "password": "correct-horse-battery",
            "date_of_birth": "1990-05-15",
        },
        format="json",
    )
    assert register_response.status_code == 201

    user = User.objects.get(username="newmember")
    assert user.is_active is False
    assert user.roles.filter(code="member").exists()

    login_before_verify = client.post(
        reverse("auth-login"),
        data={"username": "newmember", "password": "correct-horse-battery"},
        format="json",
    )
    assert login_before_verify.status_code == 401

    token_record = EmailVerificationToken.objects.get(user=user)
    verify_response = client.post(
        reverse("identity-verify-email"), data={"token": token_record.token}, format="json"
    )
    assert verify_response.status_code == 200
    user.refresh_from_db()
    assert user.is_active is True

    reused_verify = client.post(
        reverse("identity-verify-email"), data={"token": token_record.token}, format="json"
    )
    assert reused_verify.status_code == 400

    login_response = client.post(
        reverse("auth-login"),
        data={"username": "newmember", "password": "correct-horse-battery"},
        format="json",
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert "access" in body and "refresh" in body
    assert body["user"]["username"] == "newmember"

    access_token = body["access"]
    refresh_token = body["refresh"]

    me_response = client.get(
        reverse("identity-me"), HTTP_AUTHORIZATION=f"Bearer {access_token}"
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "newmember"

    refresh_response = client.post(
        reverse("auth-refresh"), data={"refresh": refresh_token}, format="json"
    )
    assert refresh_response.status_code == 200
    new_access = refresh_response.json()["access"]
    # ROTATE_REFRESH_TOKENS=True: the old refresh token is now blacklisted and a new
    # one is issued in its place, so subsequent calls must use the rotated token.
    rotated_refresh = refresh_response.json()["refresh"]

    me_again = client.get(reverse("identity-me"), HTTP_AUTHORIZATION=f"Bearer {new_access}")
    assert me_again.status_code == 200

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access}")
    logout_response = client.post(
        reverse("auth-logout"), data={"refresh": rotated_refresh}, format="json"
    )
    assert logout_response.status_code == 205

    refresh_after_logout = client.post(
        reverse("auth-refresh"), data={"refresh": rotated_refresh}, format="json"
    )
    assert refresh_after_logout.status_code == 401


@pytest.mark.django_db
def test_register_rejects_duplicate_username():
    client = APIClient()
    User.objects.create_user(username="taken", password="pass1234567")

    response = client.post(
        reverse("identity-register"),
        data={
            "username": "taken",
            "email": "other@example.com",
            "password": "another-strong-pass",
            "date_of_birth": "1990-05-15",
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_requires_date_of_birth():
    client = APIClient()

    response = client.post(
        reverse("identity-register"),
        data={
            "username": "nodobuser",
            "email": "nodob@example.com",
            "password": "another-strong-pass",
        },
        format="json",
    )
    assert response.status_code == 400
    assert "date_of_birth" in response.json()


@pytest.mark.django_db
def test_register_rejects_future_date_of_birth():
    client = APIClient()

    response = client.post(
        reverse("identity-register"),
        data={
            "username": "futuredobuser",
            "email": "futuredob@example.com",
            "password": "another-strong-pass",
            "date_of_birth": "2999-01-01",
        },
        format="json",
    )
    assert response.status_code == 400
    assert "date_of_birth" in response.json()


@pytest.mark.django_db
def test_password_reset_flow():
    user = User.objects.create_user(
        username="resetme",
        email="resetme@example.com",
        password="original-password-1",
        is_active=True,
    )
    client = APIClient()

    mail.outbox.clear()
    request_response = client.post(
        reverse("identity-password-reset-request"),
        data={"email": "resetme@example.com"},
        format="json",
    )
    assert request_response.status_code == 202

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    confirm_response = client.post(
        reverse("identity-password-reset-confirm"),
        data={"uid": uidb64, "token": token, "new_password": "brand-new-password-2"},
        format="json",
    )
    assert confirm_response.status_code == 200

    old_login = client.post(
        reverse("auth-login"),
        data={"username": "resetme", "password": "original-password-1"},
        format="json",
    )
    assert old_login.status_code == 401

    new_login = client.post(
        reverse("auth-login"),
        data={"username": "resetme", "password": "brand-new-password-2"},
        format="json",
    )
    assert new_login.status_code == 200


@pytest.mark.django_db
def test_password_reset_request_does_not_leak_account_existence():
    client = APIClient()
    response = client.post(
        reverse("identity-password-reset-request"),
        data={"email": "nobody-registered@example.com"},
        format="json",
    )
    assert response.status_code == 202


@pytest.mark.django_db
def test_register_throttles_after_limit():
    client = APIClient()
    last_status = None
    for i in range(6):
        last_status = client.post(
            reverse("identity-register"),
            data={
                "username": f"throttleuser{i}",
                "email": f"throttle{i}@example.com",
                "password": "some-strong-password-1",
                "date_of_birth": "1990-05-15",
            },
            format="json",
        ).status_code

    assert last_status == 429
