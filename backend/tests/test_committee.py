from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.membership.application.committee_service import (
    CommitteeError,
    create_committee,
    current_committee,
    remove_committee_member,
    set_committee_position,
)
from apps.membership.models import CommitteeMembership, MemberProfile
from apps.timeline.models import TimelineEntry


def _make_admin(username: str) -> User:
    user = User.objects.create_user(username=username, password="pass123")
    role, _ = Role.objects.get_or_create(code="admin", defaults={"name": "Admin"})
    user.roles.add(role)
    return user


def _admin_client():
    admin = _make_admin(f"committee-admin-{User.objects.count()}")
    client = APIClient()
    client.force_authenticate(user=admin)
    return client, admin


# -- Application layer --------------------------------------------------------


@pytest.mark.django_db
def test_create_committee_requires_a_name():
    admin = _make_admin("committee-admin-1")
    with pytest.raises(CommitteeError):
        create_committee(name="  ", starts_at=timezone.localdate(), ends_at=None, creator=admin)


@pytest.mark.django_db
def test_create_committee_rejects_end_before_start():
    admin = _make_admin("committee-admin-2")
    today = timezone.localdate()
    with pytest.raises(CommitteeError):
        create_committee(
            name="Bad Committee", starts_at=today, ends_at=today - timedelta(days=1), creator=admin
        )


@pytest.mark.django_db
def test_create_committee_creates_linked_timeline_entry():
    admin = _make_admin("committee-admin-3")
    today = timezone.localdate()
    committee = create_committee(
        name="2024-2026 Committee",
        starts_at=today,
        ends_at=today + timedelta(days=730),
        creator=admin,
    )

    entry = TimelineEntry.objects.get(committee=committee)
    assert entry.title == "2024-2026 Committee"
    assert entry.entry_date == committee.starts_at
    assert entry.end_date == committee.ends_at
    assert entry.is_published is True


@pytest.mark.django_db
def test_current_committee_returns_committee_covering_today():
    admin = _make_admin("committee-admin-4")
    today = timezone.localdate()
    committee = create_committee(
        name="Current Committee",
        starts_at=today - timedelta(days=1),
        ends_at=today + timedelta(days=1),
        creator=admin,
    )

    assert current_committee().id == committee.id


@pytest.mark.django_db
def test_current_committee_none_when_none_covers_today():
    admin = _make_admin("committee-admin-5")
    today = timezone.localdate()
    create_committee(
        name="Past Committee",
        starts_at=today - timedelta(days=10),
        ends_at=today - timedelta(days=5),
        creator=admin,
    )

    assert current_committee() is None


@pytest.mark.django_db
def test_committee_with_no_end_date_is_ongoing_and_current():
    admin = _make_admin("committee-admin-6")
    today = timezone.localdate()
    committee = create_committee(name="Ongoing Committee", starts_at=today, ends_at=None, creator=admin)

    assert current_committee().id == committee.id


@pytest.mark.django_db
def test_set_committee_position_derives_display_order_from_rank():
    admin = _make_admin("committee-admin-7")
    member = User.objects.create_user(username="committee-member-1", password="pass123")
    today = timezone.localdate()
    committee = create_committee(name="Committee A", starts_at=today, ends_at=None, creator=admin)

    membership = set_committee_position(committee=committee, user=member, position="Vice President")

    assert membership.position == "Vice President"
    # Advisors(0), President(1), Senior Vice President(2), Vice President(3)
    assert membership.display_order == 3


@pytest.mark.django_db
def test_set_committee_position_is_idempotent_upsert():
    admin = _make_admin("committee-admin-8")
    member = User.objects.create_user(username="committee-member-2", password="pass123")
    today = timezone.localdate()
    committee = create_committee(name="Committee B", starts_at=today, ends_at=None, creator=admin)

    set_committee_position(committee=committee, user=member, position="President")
    set_committee_position(committee=committee, user=member, position="General Secretary")

    assert CommitteeMembership.objects.filter(committee=committee, user=member).count() == 1
    membership = CommitteeMembership.objects.get(committee=committee, user=member)
    assert membership.position == "General Secretary"


@pytest.mark.django_db
def test_remove_committee_member():
    admin = _make_admin("committee-admin-9")
    member = User.objects.create_user(username="committee-member-3", password="pass123")
    today = timezone.localdate()
    committee = create_committee(name="Committee C", starts_at=today, ends_at=None, creator=admin)
    set_committee_position(committee=committee, user=member, position="President")

    remove_committee_member(committee=committee, user=member)

    assert not CommitteeMembership.objects.filter(committee=committee, user=member).exists()


# -- REST API -------------------------------------------------------------------


@pytest.mark.django_db
def test_committee_create_endpoint_requires_admin_role():
    member = User.objects.create_user(username="not-admin-committee-1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("membership-committees"),
        data={"name": "New Committee", "starts_at": str(timezone.localdate())},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_committee_create_endpoint_succeeds_for_admin():
    client, admin = _admin_client()
    today = timezone.localdate()

    response = client.post(
        reverse("membership-committees"),
        data={"name": "2026 Committee", "starts_at": str(today)},
        format="json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "2026 Committee"
    assert body["is_current"] is True


@pytest.mark.django_db
def test_committee_members_endpoint_requires_admin_role_to_post():
    non_admin = User.objects.create_user(username="not-admin-committee-2", password="pass123")
    target = User.objects.create_user(username="committee-member-4", password="pass123")
    admin = _make_admin("committee-admin-10")
    today = timezone.localdate()
    committee = create_committee(name="Committee D", starts_at=today, ends_at=None, creator=admin)

    client = APIClient()
    client.force_authenticate(user=non_admin)
    response = client.post(
        reverse("membership-committee-members", kwargs={"committee_id": committee.id}),
        data={"user_id": str(target.id), "position": "President"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_committee_members_endpoint_rejects_free_text_position():
    client, admin = _admin_client()
    target = User.objects.create_user(username="committee-member-5", password="pass123")
    today = timezone.localdate()
    committee = create_committee(name="Committee E", starts_at=today, ends_at=None, creator=admin)

    response = client.post(
        reverse("membership-committee-members", kwargs={"committee_id": committee.id}),
        data={"user_id": str(target.id), "position": "Made Up Title"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_committee_members_endpoint_lists_roster():
    client, admin = _admin_client()
    target = User.objects.create_user(
        username="committee-member-6", first_name="Rina", password="pass123"
    )
    today = timezone.localdate()
    committee = create_committee(name="Committee F", starts_at=today, ends_at=None, creator=admin)
    set_committee_position(committee=committee, user=target, position="President")

    response = client.get(
        reverse("membership-committee-members", kwargs={"committee_id": committee.id})
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["position"] == "President"
    assert body[0]["name"] == "Rina"


@pytest.mark.django_db
def test_committee_member_remove_endpoint():
    client, admin = _admin_client()
    target = User.objects.create_user(username="committee-member-7", password="pass123")
    today = timezone.localdate()
    committee = create_committee(name="Committee G", starts_at=today, ends_at=None, creator=admin)
    set_committee_position(committee=committee, user=target, position="President")

    response = client.post(
        reverse(
            "membership-committee-member-remove",
            kwargs={"committee_id": committee.id, "user_id": target.id},
        )
    )

    assert response.status_code == 204
    assert not CommitteeMembership.objects.filter(committee=committee, user=target).exists()


@pytest.mark.django_db
def test_public_committee_roster_view_returns_past_committee():
    """Confirms past committees stay browsable — reachable by id even long after
    they've stopped being "current", which is what makes them accessible from
    their timeline entry."""
    admin = _make_admin("committee-admin-11")
    target = User.objects.create_user(username="committee-member-8", password="pass123")
    MemberProfile.objects.create(user=target, public_consent=True)
    today = timezone.localdate()
    past_committee = create_committee(
        name="2020-2022 Committee",
        starts_at=today - timedelta(days=1000),
        ends_at=today - timedelta(days=500),
        creator=admin,
    )
    set_committee_position(committee=past_committee, user=target, position="President")

    client = APIClient()
    response = client.get(
        reverse("membership-committee-public-roster", kwargs={"committee_id": past_committee.id})
    )

    assert response.status_code == 200
    body = response.json()
    assert body["committee"]["name"] == "2020-2022 Committee"
    assert body["committee"]["is_current"] is False
    assert len(body["members"]) == 1
    assert body["members"][0]["position"] == "President"


@pytest.mark.django_db
def test_public_committee_roster_hides_non_consenting_members():
    admin = _make_admin("committee-admin-12")
    target = User.objects.create_user(username="committee-member-9", password="pass123")
    MemberProfile.objects.create(user=target, public_consent=False)
    today = timezone.localdate()
    committee = create_committee(name="Committee H", starts_at=today, ends_at=None, creator=admin)
    set_committee_position(committee=committee, user=target, position="President")

    client = APIClient()
    response = client.get(
        reverse("membership-committee-public-roster", kwargs={"committee_id": committee.id})
    )

    assert response.status_code == 200
    assert response.json()["members"] == []


@pytest.mark.django_db
def test_public_roster_view_shows_current_committee_and_splits_members():
    admin = _make_admin("committee-admin-13")
    today = timezone.localdate()

    committee_member = User.objects.create_user(
        username="roster-committee-1", email="chair@example.com", password="pass123"
    )
    MemberProfile.objects.create(user=committee_member, public_consent=True)
    committee = create_committee(name="Current Committee", starts_at=today, ends_at=None, creator=admin)
    set_committee_position(committee=committee, user=committee_member, position="President")

    plain_member = User.objects.create_user(
        username="roster-member-1", email="member@example.com", password="pass123"
    )
    MemberProfile.objects.create(user=plain_member, public_consent=True)

    non_consenting = User.objects.create_user(username="roster-hidden-1", password="pass123")
    MemberProfile.objects.create(user=non_consenting, public_consent=False)
    set_committee_position(committee=committee, user=non_consenting, position="General Secretary")

    client = APIClient()
    response = client.get(reverse("membership-profile-public"))

    assert response.status_code == 200
    body = response.json()
    committee_positions = {item["position"] for item in body["committee"]}
    assert committee_positions == {"President"}
    assert len(body["members"]) == 1
    assert len(body["committee"]) == 1
