import uuid
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.events.domain.status import (
    REG_STATUS_ATTENDED,
    REG_STATUS_REGISTERED,
    REG_STATUS_WAITLISTED,
)
from apps.events.models import Event, EventRegistration
from apps.identity.models import Role, User
from apps.membership.domain.status import STATUS_ACTIVE, STATUS_PENDING
from apps.membership.models import Membership


@pytest.mark.django_db
def test_events_list_returns_only_published_events():
    creator = User.objects.create_user(username="creator1", password="pass123")
    now = timezone.now()

    Event.objects.create(
        title="Public Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )
    Event.objects.create(
        title="Draft Event",
        starts_at=now + timedelta(days=2),
        ends_at=now + timedelta(days=2, hours=2),
        is_published=False,
        created_by=creator,
    )

    client = APIClient()
    response = client.get(reverse("events-list-create"))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Public Event"


@pytest.mark.django_db
def test_events_create_requires_admin_or_volunteer_role():
    user = User.objects.create_user(username="plain-user", password="pass123")
    now = timezone.now()
    payload = {
        "title": "Role-Gated Event",
        "starts_at": (now + timedelta(days=1)).isoformat(),
        "ends_at": (now + timedelta(days=1, hours=1)).isoformat(),
        "is_published": True,
    }

    client = APIClient()
    client.force_authenticate(user=user)
    forbidden = client.post(reverse("events-list-create"), data=payload, format="json")
    assert forbidden.status_code == 403

    volunteer = Role.objects.create(code="volunteer", name="Volunteer")
    user.roles.add(volunteer)
    allowed = client.post(reverse("events-list-create"), data=payload, format="json")
    assert allowed.status_code == 201


@pytest.mark.django_db
def test_register_event_requires_active_membership():
    now = timezone.now()
    creator = User.objects.create_user(username="creator2", password="pass123")
    event = Event.objects.create(
        title="Membership Only Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )

    user = User.objects.create_user(username="pending-member", password="pass123")
    Membership.objects.create(user=user, status=STATUS_PENDING)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        reverse("events-register"),
        data={"event_id": str(event.id)},
        format="json",
    )

    assert response.status_code == 400
    assert "active members" in response.json()["detail"].lower()


@pytest.mark.django_db
def test_register_event_and_check_in_success_flow():
    now = timezone.now()
    creator = User.objects.create_user(username="creator3", password="pass123")
    event = Event.objects.create(
        title="Check-In Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )

    attendee = User.objects.create_user(username="attendee1", password="pass123")
    Membership.objects.create(user=attendee, status=STATUS_ACTIVE)

    client = APIClient()
    client.force_authenticate(user=attendee)
    reg_response = client.post(
        reverse("events-register"),
        data={"event_id": str(event.id)},
        format="json",
    )
    assert reg_response.status_code == 201
    registration_id = reg_response.json()["id"]

    no_role_check_in = client.post(
        reverse("events-check-in"),
        data={"registration_id": registration_id},
        format="json",
    )
    assert no_role_check_in.status_code == 403

    volunteer_role = Role.objects.create(code="volunteer", name="Volunteer")
    attendee.roles.add(volunteer_role)

    check_in_response = client.post(
        reverse("events-check-in"),
        data={"registration_id": registration_id},
        format="json",
    )

    assert check_in_response.status_code == 200
    assert check_in_response.json()["status"] == REG_STATUS_ATTENDED

    registration = EventRegistration.objects.get(id=registration_id)
    assert registration.status == REG_STATUS_ATTENDED


@pytest.mark.django_db
def test_duplicate_registration_is_blocked():
    now = timezone.now()
    creator = User.objects.create_user(username="creator4", password="pass123")
    event = Event.objects.create(
        title="Duplicate Guard Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )

    attendee = User.objects.create_user(username="attendee2", password="pass123")
    Membership.objects.create(user=attendee, status=STATUS_ACTIVE)

    client = APIClient()
    client.force_authenticate(user=attendee)

    first = client.post(reverse("events-register"), data={"event_id": str(event.id)}, format="json")
    assert first.status_code == 201

    second = client.post(reverse("events-register"), data={"event_id": str(event.id)}, format="json")
    assert second.status_code == 400
    assert "already registered" in second.json()["detail"].lower()


@pytest.mark.django_db
def test_cancel_event_soft_deletes_and_preserves_registrations():
    now = timezone.now()
    admin = User.objects.create_user(username="event-admin-1", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    event = Event.objects.create(
        title="Cancel Me",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=admin,
    )

    attendee = User.objects.create_user(username="attendee3", password="pass123")
    Membership.objects.create(user=attendee, status=STATUS_ACTIVE)

    client = APIClient()
    client.force_authenticate(user=attendee)
    reg_response = client.post(
        reverse("events-register"), data={"event_id": str(event.id)}, format="json"
    )
    assert reg_response.status_code == 201
    registration_id = reg_response.json()["id"]

    client.force_authenticate(user=admin)
    cancel_response = client.post(reverse("events-cancel", kwargs={"event_id": event.id}))
    assert cancel_response.status_code == 200
    assert cancel_response.json()["is_published"] is False

    assert Event.objects.filter(id=event.id).count() == 0
    soft_deleted = Event.all_objects.get(id=event.id)
    assert soft_deleted.deleted_at is not None

    listing = client.get(reverse("events-list-create"))
    assert all(item["title"] != "Cancel Me" for item in listing.json())

    assert EventRegistration.objects.filter(id=registration_id).exists()


@pytest.mark.django_db
def test_cancel_event_requires_role():
    now = timezone.now()
    creator = User.objects.create_user(username="creator5", password="pass123")
    plain_user = User.objects.create_user(username="plain-user-2", password="pass123")
    event = Event.objects.create(
        title="Protected Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )

    client = APIClient()
    client.force_authenticate(user=plain_user)
    response = client.post(reverse("events-cancel", kwargs={"event_id": event.id}))

    assert response.status_code == 403
    assert Event.objects.filter(id=event.id).count() == 1


@pytest.mark.django_db
def test_register_beyond_capacity_is_waitlisted():
    now = timezone.now()
    creator = User.objects.create_user(username="creator6", password="pass123")
    event = Event.objects.create(
        title="Small Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        capacity=1,
        created_by=creator,
    )

    first_attendee = User.objects.create_user(username="attendee-first", password="pass123")
    Membership.objects.create(user=first_attendee, status=STATUS_ACTIVE)
    second_attendee = User.objects.create_user(username="attendee-second", password="pass123")
    Membership.objects.create(user=second_attendee, status=STATUS_ACTIVE)

    client = APIClient()

    client.force_authenticate(user=first_attendee)
    first_response = client.post(
        reverse("events-register"), data={"event_id": str(event.id)}, format="json"
    )
    assert first_response.status_code == 201
    assert first_response.json()["status"] == REG_STATUS_REGISTERED

    client.force_authenticate(user=second_attendee)
    second_response = client.post(
        reverse("events-register"), data={"event_id": str(event.id)}, format="json"
    )
    assert second_response.status_code == 201
    assert second_response.json()["status"] == REG_STATUS_WAITLISTED


@pytest.mark.django_db
def test_cancel_registration_promotes_oldest_waitlisted():
    now = timezone.now()
    creator = User.objects.create_user(username="creator7", password="pass123")
    event = Event.objects.create(
        title="Promotion Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        capacity=1,
        created_by=creator,
    )

    confirmed = User.objects.create_user(username="confirmed-attendee", password="pass123")
    Membership.objects.create(user=confirmed, status=STATUS_ACTIVE)
    waitlisted = User.objects.create_user(username="waitlisted-attendee", password="pass123")
    Membership.objects.create(user=waitlisted, status=STATUS_ACTIVE)

    client = APIClient()
    client.force_authenticate(user=confirmed)
    confirmed_response = client.post(
        reverse("events-register"), data={"event_id": str(event.id)}, format="json"
    )
    confirmed_registration_id = confirmed_response.json()["id"]

    client.force_authenticate(user=waitlisted)
    client.post(reverse("events-register"), data={"event_id": str(event.id)}, format="json")
    waitlisted_registration = EventRegistration.objects.get(event=event, user=waitlisted)
    assert waitlisted_registration.status == REG_STATUS_WAITLISTED

    client.force_authenticate(user=confirmed)
    cancel_response = client.post(
        reverse("events-registration-cancel", kwargs={"registration_id": confirmed_registration_id})
    )
    assert cancel_response.status_code == 200

    waitlisted_registration.refresh_from_db()
    assert waitlisted_registration.status == REG_STATUS_REGISTERED


@pytest.mark.django_db
def test_cancel_registration_requires_owner_or_role():
    now = timezone.now()
    creator = User.objects.create_user(username="creator8", password="pass123")
    event = Event.objects.create(
        title="Auth Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )

    owner = User.objects.create_user(username="reg-owner", password="pass123")
    Membership.objects.create(user=owner, status=STATUS_ACTIVE)
    stranger = User.objects.create_user(username="reg-stranger", password="pass123")

    client = APIClient()
    client.force_authenticate(user=owner)
    reg_response = client.post(
        reverse("events-register"), data={"event_id": str(event.id)}, format="json"
    )
    registration_id = reg_response.json()["id"]

    client.force_authenticate(user=stranger)
    forbidden = client.post(
        reverse("events-registration-cancel", kwargs={"registration_id": registration_id})
    )
    assert forbidden.status_code == 400

    client.force_authenticate(user=owner)
    allowed = client.post(
        reverse("events-registration-cancel", kwargs={"registration_id": registration_id})
    )
    assert allowed.status_code == 200


@pytest.mark.django_db
def test_check_in_via_qr_token():
    now = timezone.now()
    creator = User.objects.create_user(username="creator9", password="pass123")
    volunteer = User.objects.create_user(username="qr-volunteer", password="pass123")
    Role.objects.create(code="volunteer", name="Volunteer").users.add(volunteer)

    event = Event.objects.create(
        title="QR Event",
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=2),
        is_published=True,
        created_by=creator,
    )
    attendee = User.objects.create_user(username="qr-attendee", password="pass123")
    Membership.objects.create(user=attendee, status=STATUS_ACTIVE)

    client = APIClient()
    client.force_authenticate(user=attendee)
    reg_response = client.post(
        reverse("events-register"), data={"event_id": str(event.id)}, format="json"
    )
    qr_token = reg_response.json()["qr_token"]

    client.force_authenticate(user=volunteer)
    check_in_response = client.post(
        reverse("events-check-in"), data={"qr_token": qr_token}, format="json"
    )
    assert check_in_response.status_code == 200
    assert check_in_response.json()["status"] == REG_STATUS_ATTENDED


@pytest.mark.django_db
def test_check_in_requires_exactly_one_identifier():
    volunteer = User.objects.create_user(username="qr-volunteer-2", password="pass123")
    Role.objects.create(code="volunteer", name="Volunteer").users.add(volunteer)

    client = APIClient()
    client.force_authenticate(user=volunteer)

    neither = client.post(reverse("events-check-in"), data={}, format="json")
    assert neither.status_code == 400

    both = client.post(
        reverse("events-check-in"),
        data={"registration_id": str(uuid.uuid4()), "qr_token": str(uuid.uuid4())},
        format="json",
    )
    assert both.status_code == 400
