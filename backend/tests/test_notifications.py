import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.notifications.application.dispatch_service import (
    dispatch_notification,
    queue_notification,
)
from apps.notifications.domain.types import (
    CHANNEL_PUSH,
    CHANNEL_WHATSAPP,
    STATUS_FAILED,
    STATUS_SENT,
)
from apps.notifications.infrastructure.adapters import (
    WebPushNotificationAdapter,
    WhatsAppNotificationAdapter,
)
from apps.notifications.models import Notification, PushSubscription


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


@pytest.mark.django_db
def test_push_subscription_register_then_unregister():
    user = User.objects.create_user(username="push-user-1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    register_response = client.post(
        reverse("notifications-push-subscribe"),
        data={
            "endpoint": "https://push.example.com/subscription/abc",
            "p256dh_key": "p256dh-value",
            "auth_key": "auth-value",
        },
        format="json",
    )
    assert register_response.status_code == 201
    subscription = PushSubscription.objects.get(user=user)
    assert subscription.is_active is True

    unregister_response = client.post(
        reverse("notifications-push-unsubscribe"),
        data={"endpoint": "https://push.example.com/subscription/abc"},
        format="json",
    )
    assert unregister_response.status_code == 204
    subscription.refresh_from_db()
    assert subscription.is_active is False


@pytest.mark.django_db
def test_webpush_adapter_sends_to_all_active_subscriptions(monkeypatch):
    user = User.objects.create_user(username="push-user-2", password="pass123")
    PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/subscription/1",
        p256dh_key="key1",
        auth_key="auth1",
    )
    PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/subscription/2",
        p256dh_key="key2",
        auth_key="auth2",
    )

    sent_endpoints = []
    monkeypatch.setattr(
        "apps.notifications.infrastructure.adapters.webpush",
        lambda subscription_info, **kwargs: sent_endpoints.append(subscription_info["endpoint"]),
    )

    WebPushNotificationAdapter().send(recipient=user, subject="Hi", body="Body", context={})

    assert set(sent_endpoints) == {
        "https://push.example.com/subscription/1",
        "https://push.example.com/subscription/2",
    }


@pytest.mark.django_db
def test_webpush_adapter_raises_without_active_subscriptions():
    user = User.objects.create_user(username="push-user-3", password="pass123")

    with pytest.raises(ValueError):
        WebPushNotificationAdapter().send(recipient=user, subject="Hi", body="Body", context={})


@pytest.mark.django_db
def test_whatsapp_adapter_posts_to_business_api(monkeypatch, settings):
    settings.WHATSAPP_API_TOKEN = "test-token"
    settings.WHATSAPP_PHONE_NUMBER_ID = "1234567890"
    user = User.objects.create_user(
        username="whatsapp-user-1", password="pass123", phone_number="+441234567890"
    )

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("apps.notifications.infrastructure.adapters.requests.post", fake_post)

    WhatsAppNotificationAdapter().send(
        recipient=user, subject="", body="Your dues are due", context={}
    )

    assert captured["json"]["to"] == "+441234567890"
    assert captured["json"]["text"]["body"] == "Your dues are due"
    assert "1234567890" in captured["url"]


@pytest.mark.django_db
def test_whatsapp_adapter_raises_without_phone_number(settings):
    settings.WHATSAPP_API_TOKEN = "test-token"
    settings.WHATSAPP_PHONE_NUMBER_ID = "1234567890"
    user = User.objects.create_user(username="whatsapp-user-2", password="pass123")

    with pytest.raises(ValueError):
        WhatsAppNotificationAdapter().send(recipient=user, subject="", body="Body", context={})


@pytest.mark.django_db
def test_queue_notification_with_dedup_key_skips_duplicate_when_pending():
    user = User.objects.create_user(username="dedup-user-1", password="pass123")

    first = queue_notification(
        recipient=user, channel="email", body="Reminder", dedup_key="event-42-reminder"
    )
    second = queue_notification(
        recipient=user, channel="email", body="Reminder", dedup_key="event-42-reminder"
    )

    assert first.id == second.id
    assert Notification.objects.filter(dedup_key="event-42-reminder").count() == 1


@pytest.mark.django_db
def test_dispatch_notification_records_failure_and_reraises(monkeypatch):
    user = User.objects.create_user(username="dispatch-fail-user", password="pass123")
    notification = queue_notification(recipient=user, channel=CHANNEL_PUSH, body="Body")

    monkeypatch.setattr(
        "apps.notifications.infrastructure.adapters.WebPushNotificationAdapter.send",
        lambda self, **kwargs: (_ for _ in ()).throw(ValueError("no subscriptions")),
    )

    with pytest.raises(ValueError):
        dispatch_notification(notification)

    notification.refresh_from_db()
    assert notification.status == STATUS_FAILED
    assert notification.attempts == 1
    assert "no subscriptions" in notification.error_message


@pytest.mark.django_db
def test_dispatch_notification_success_marks_sent_and_increments_attempts(monkeypatch):
    user = User.objects.create_user(
        username="dispatch-ok-user", password="pass123", phone_number="+441234567890"
    )
    notification = queue_notification(recipient=user, channel=CHANNEL_WHATSAPP, body="Body")

    monkeypatch.setattr(
        "apps.notifications.infrastructure.adapters.WhatsAppNotificationAdapter.send",
        lambda self, **kwargs: None,
    )

    dispatch_notification(notification)

    notification.refresh_from_db()
    assert notification.status == STATUS_SENT
    assert notification.attempts == 1
    assert notification.sent_at is not None
