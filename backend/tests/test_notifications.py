import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.notifications.models import Notification


@pytest.mark.django_db
def test_notifications_me_requires_authentication():
    client = APIClient()
    response = client.get(reverse("notifications-me"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_notifications_send_requires_admin_or_volunteer(monkeypatch):
    sender = User.objects.create_user(username="sender1", password="pass123")
    recipient = User.objects.create_user(username="recipient1", password="pass123")

    monkeypatch.setattr(
        "apps.notifications.application.notification_orchestrator.dispatch_notification_task.delay",
        lambda _notification_id: None,
    )

    client = APIClient()
    client.force_authenticate(user=sender)

    response = client.post(
        reverse("notifications-send"),
        data={
            "recipient_id": str(recipient.id),
            "channel": "email",
            "subject": "Test",
            "body": "Hello",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_notifications_send_creates_queued_notification(monkeypatch):
    sender = User.objects.create_user(username="sender2", password="pass123")
    recipient = User.objects.create_user(username="recipient2", password="pass123")
    volunteer = Role.objects.create(code="volunteer", name="Volunteer")
    sender.roles.add(volunteer)

    monkeypatch.setattr(
        "apps.notifications.application.notification_orchestrator.dispatch_notification_task.delay",
        lambda _notification_id: None,
    )

    client = APIClient()
    client.force_authenticate(user=sender)

    response = client.post(
        reverse("notifications-send"),
        data={
            "recipient_id": str(recipient.id),
            "channel": "email",
            "subject": "Event update",
            "body": "Your event starts soon.",
            "context": {"source": "test"},
        },
        format="json",
    )

    assert response.status_code == 201
    created = Notification.objects.get(id=response.json()["id"])
    assert created.recipient == recipient
    assert created.channel == "email"
    assert created.status == "queued"


@pytest.mark.django_db
def test_notifications_me_lists_user_notifications(monkeypatch):
    user = User.objects.create_user(username="recipient3", password="pass123")

    monkeypatch.setattr(
        "apps.notifications.application.notification_orchestrator.dispatch_notification_task.delay",
        lambda _notification_id: None,
    )

    Notification.objects.create(recipient=user, channel="email", subject="A", body="Body A")
    Notification.objects.create(recipient=user, channel="push", subject="B", body="Body B")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(reverse("notifications-me"))

    assert response.status_code == 200
    assert len(response.json()) == 2
