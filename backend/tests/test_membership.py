from io import StringIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from apps.common.models import AuditLog
from apps.identity.models import Role, User
from apps.membership.domain.status import STATUS_ACTIVE, STATUS_CANCELLED, STATUS_PENDING
from apps.membership.models import Membership, MembershipStatusTransition, MemberProfile


@pytest.fixture(autouse=True)
def _mock_object_storage(monkeypatch):
    store: dict[str, bytes] = {}

    def fake_upload_bytes(*, key, data, content_type):
        store[key] = data

    def fake_download_bytes(*, key):
        return store[key]

    monkeypatch.setattr("apps.media.application.image_service.storage.upload_bytes", fake_upload_bytes)
    monkeypatch.setattr(
        "apps.media.application.image_service.storage.download_bytes", fake_download_bytes
    )
    yield


def _admin_client() -> tuple[APIClient, User]:
    admin_user = User.objects.create_user(username=f"admin-{User.objects.count()}", password="pass123")
    admin_role, _ = Role.objects.get_or_create(code="admin", defaults={"name": "Admin"})
    admin_user.roles.add(admin_role)
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client, admin_user


def _photo(name: str = "photo.jpg") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"fake-image-bytes", content_type="image/jpeg")


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


@pytest.mark.django_db
def test_member_directory_requires_admin_or_volunteer_role():
    member = User.objects.create_user(username="plain-directory-user", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.get(reverse("membership-directory"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_member_directory_available_to_volunteer_and_filters_by_search():
    volunteer = User.objects.create_user(username="directory-volunteer", password="pass123")
    Role.objects.create(code="volunteer", name="Volunteer").users.add(volunteer)

    alice = User.objects.create_user(username="alice-dir", first_name="Alice", password="pass123")
    MemberProfile.objects.create(user=alice, avatar_url="https://example.com/alice.jpg")
    User.objects.create_user(username="bob-dir", first_name="Bob", password="pass123")
    inactive = User.objects.create_user(
        username="inactive-dir", first_name="Ivy", password="pass123", is_active=False
    )

    client = APIClient()
    client.force_authenticate(user=volunteer)

    response = client.get(reverse("membership-directory"), {"q": "alice"})
    assert response.status_code == 200
    usernames = {row["username"] for row in response.json()}
    assert usernames == {"alice-dir"}
    assert response.json()[0]["avatar_url"] == "https://example.com/alice.jpg"

    all_response = client.get(reverse("membership-directory"))
    all_usernames = {row["username"] for row in all_response.json()}
    assert inactive.username not in all_usernames


@pytest.mark.django_db
def test_membership_admin_list_includes_phone_and_avatar():
    client, _ = _admin_client()

    member = User.objects.create_user(
        username="carol-contact", password="pass123", phone_number="+44 7700 900200"
    )
    Membership.objects.create(user=member, status=STATUS_ACTIVE)
    MemberProfile.objects.create(user=member, avatar_url="https://example.com/carol.jpg")

    response = client.get(reverse("membership-admin-list"))
    assert response.status_code == 200

    row = next(item for item in response.json()["results"] if item["username"] == "carol-contact")
    assert row["phone_number"] == "+44 7700 900200"
    assert row["avatar_url"] == "https://example.com/carol.jpg"
    assert row["is_active"] is True


@pytest.mark.django_db
def test_my_profile_photo_upload_succeeds_for_any_member():
    # Regression: this endpoint (not the admin/volunteer-gated media upload
    # endpoint) is what the member profile page's photo field must call.
    member = User.objects.create_user(username="plain-uploader", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("membership-profile-photo"),
        data={"file": _photo()},
        format="multipart",
    )

    assert response.status_code == 201
    assert response.json()["url"]
    member.refresh_from_db()
    assert member.profile.avatar_url == response.json()["url"]


@pytest.mark.django_db
def test_admin_create_member_requires_role():
    member = User.objects.create_user(username="not-admin", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("membership-admin-create"),
        data={
            "username": "walkin",
            "email": "walkin@example.com",
            "date_of_birth": "1990-01-01",
            "phone_number": "+44 7700 900201",
            "avatar_url": "https://example.com/walkin.jpg",
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_create_member_creates_user_membership_and_profile():
    client, _ = _admin_client()

    response = client.post(
        reverse("membership-admin-create"),
        data={
            "username": "walkin2",
            "email": "walkin2@example.com",
            "first_name": "Walk",
            "last_name": "In",
            "date_of_birth": "1990-01-01",
            "phone_number": "+44 7700 900202",
            "avatar_url": "https://example.com/walkin2.jpg",
        },
        format="json",
    )
    assert response.status_code == 201

    created = User.objects.get(username="walkin2")
    assert created.is_active is True
    assert created.phone_number == "+44 7700 900202"
    assert created.has_usable_password() is False
    assert created.roles.filter(code="member").exists()
    assert Membership.objects.filter(user=created).exists()
    assert created.profile.avatar_url == "https://example.com/walkin2.jpg"


@pytest.mark.django_db
def test_admin_create_member_requires_phone_and_photo():
    client, _ = _admin_client()

    missing_phone = client.post(
        reverse("membership-admin-create"),
        data={
            "username": "walkin3",
            "email": "walkin3@example.com",
            "date_of_birth": "1990-01-01",
            "avatar_url": "https://example.com/walkin3.jpg",
        },
        format="json",
    )
    assert missing_phone.status_code == 400

    missing_photo = client.post(
        reverse("membership-admin-create"),
        data={
            "username": "walkin4",
            "email": "walkin4@example.com",
            "date_of_birth": "1990-01-01",
            "phone_number": "+44 7700 900203",
        },
        format="json",
    )
    assert missing_photo.status_code == 400
    assert not User.objects.filter(username="walkin4").exists()


@pytest.mark.django_db
def test_admin_update_member_contact_requires_role():
    member = User.objects.create_user(username="not-admin-2", password="pass123")
    target = User.objects.create_user(username="target-contact", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("membership-admin-contact"),
        data={"user_id": str(target.id), "phone_number": "+44 7700 900204"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_update_member_contact_updates_phone_and_avatar():
    client, _ = _admin_client()
    target = User.objects.create_user(username="target-contact-2", password="pass123")

    response = client.post(
        reverse("membership-admin-contact"),
        data={
            "user_id": str(target.id),
            "phone_number": "+44 7700 900205",
            "avatar_url": "https://example.com/target.jpg",
        },
        format="json",
    )

    assert response.status_code == 200
    target.refresh_from_db()
    assert target.phone_number == "+44 7700 900205"
    assert target.profile.avatar_url == "https://example.com/target.jpg"


@pytest.mark.django_db
def test_admin_set_member_active_requires_role():
    member = User.objects.create_user(username="not-admin-3", password="pass123")
    target = User.objects.create_user(username="target-active", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("membership-admin-active"),
        data={"user_id": str(target.id), "is_active": False},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_set_member_active_deactivates_and_reactivates():
    client, _ = _admin_client()
    target = User.objects.create_user(username="target-active-2", password="pass123", is_active=True)

    deactivate_response = client.post(
        reverse("membership-admin-active"),
        data={"user_id": str(target.id), "is_active": False},
        format="json",
    )
    assert deactivate_response.status_code == 200
    target.refresh_from_db()
    assert target.is_active is False

    reactivate_response = client.post(
        reverse("membership-admin-active"),
        data={"user_id": str(target.id), "is_active": True},
        format="json",
    )
    assert reactivate_response.status_code == 200
    target.refresh_from_db()
    assert target.is_active is True


@pytest.mark.django_db
def test_admin_erase_member_requires_role():
    member = User.objects.create_user(username="not-admin-4", password="pass123")
    target = User.objects.create_user(username="target-erase", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("membership-admin-erase"), data={"user_id": str(target.id)}, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_erase_member_rejects_self_erase():
    client, admin = _admin_client()

    response = client.post(
        reverse("membership-admin-erase"), data={"user_id": str(admin.id)}, format="json"
    )
    assert response.status_code == 400
    admin.refresh_from_db()
    assert admin.username != f"deleted-{admin.id.hex[:12]}"


@pytest.mark.django_db
def test_admin_erase_member_returns_404_for_unknown_user():
    client, _ = _admin_client()
    response = client.post(
        reverse("membership-admin-erase"),
        data={"user_id": "00000000-0000-0000-0000-000000000000"},
        format="json",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_admin_erase_member_scrubs_pii_but_keeps_related_records(monkeypatch):
    deleted_keys = []
    monkeypatch.setattr(
        "apps.membership.application.member_admin_service.delete_object",
        lambda *, key: deleted_keys.append(key),
    )

    client, admin = _admin_client()
    target = User.objects.create_user(
        username="erase-me",
        email="erase-me@example.com",
        first_name="Erin",
        last_name="Ashe",
        password="pass123",
        phone_number="+44 7700 900300",
        is_active=True,
    )
    membership = Membership.objects.create(user=target, status=STATUS_ACTIVE)
    MemberProfile.objects.create(
        user=target,
        avatar_url="https://example.com/media/images/erase-me.jpg",
        bio="Loves gardening",
        position="Secretary",
        public_consent=True,
    )

    response = client.post(
        reverse("membership-admin-erase"), data={"user_id": str(target.id)}, format="json"
    )
    assert response.status_code == 204

    target.refresh_from_db()
    assert target.username == f"deleted-{target.id.hex[:12]}"
    assert target.email == ""
    assert target.first_name == ""
    assert target.last_name == ""
    assert target.phone_number == ""
    assert target.date_of_birth is None
    assert target.is_active is False
    assert target.has_usable_password() is False

    target.profile.refresh_from_db()
    assert target.profile.avatar_url == ""
    assert target.profile.bio == ""
    assert target.profile.position == ""
    assert target.profile.public_consent is False

    # The membership row itself (financial/history record) must survive, still
    # pointing at the same (now-anonymized) user.
    membership.refresh_from_db()
    assert membership.user_id == target.id
    assert Membership.objects.filter(id=membership.id).exists()

    assert deleted_keys == ["images/erase-me.jpg"]


@pytest.mark.django_db
def test_admin_erase_member_writes_audit_log(monkeypatch):
    monkeypatch.setattr(
        "apps.membership.application.member_admin_service.delete_object", lambda *, key: None
    )
    client, admin = _admin_client()
    target = User.objects.create_user(username="erase-audit", password="pass123")

    client.post(reverse("membership-admin-erase"), data={"user_id": str(target.id)}, format="json")

    entry = AuditLog.objects.get(action="member_erased", entity_id=str(target.id))
    assert entry.actor_id == admin.id
    assert entry.entity_type == "User"
