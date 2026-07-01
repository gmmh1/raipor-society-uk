from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.events.domain.status import REG_STATUS_ATTENDED, REG_STATUS_REGISTERED
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
