import requests
from django.conf import settings
from django.core.mail import send_mail
from pywebpush import WebPushException, webpush

from apps.notifications.domain.types import CHANNEL_EMAIL, CHANNEL_PUSH, CHANNEL_WHATSAPP


class NotificationAdapter:
    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:
        raise NotImplementedError  # pragma: no cover - interface


class NoopNotificationAdapter(NotificationAdapter):
    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:
        # Intentionally no-op: no real integration exists yet for this channel.
        return None


class EmailNotificationAdapter(NotificationAdapter):
    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:
        if recipient is None or not getattr(recipient, "email", ""):
            raise ValueError("Recipient has no email address to send to.")

        send_mail(
            subject=subject or "Raipur Society UK",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )


class WebPushNotificationAdapter(NotificationAdapter):
    """Sends via the W3C Web Push standard (VAPID), not a vendor push SDK.

    Native mobile push (FCM/APNs) is deliberately out of scope — see ADR 0013.
    """

    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:
        if recipient is None:
            raise ValueError("Recipient is required to send a push notification.")

        subscriptions = list(recipient.push_subscriptions.filter(is_active=True))
        if not subscriptions:
            raise ValueError("Recipient has no active push subscriptions.")

        payload = {"title": subject or "Raipur Society UK", "body": body}
        last_error: Exception | None = None
        delivered = False

        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh_key,
                            "auth": subscription.auth_key,
                        },
                    },
                    data=str(payload),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIM_EMAIL}"},
                )
                delivered = True
            except WebPushException as exc:
                response = getattr(exc, "response", None)
                if response is not None and response.status_code in (404, 410):
                    subscription.is_active = False
                    subscription.save(update_fields=["is_active", "updated_at"])
                last_error = exc

        if not delivered and last_error is not None:
            raise last_error


class WhatsAppNotificationAdapter(NotificationAdapter):
    """Sends via the WhatsApp Business Cloud API (Meta).

    No open-source self-hosted alternative exists for WhatsApp delivery; this is an
    intentional, isolated exception to the "avoid vendor lock-in" preference because
    WhatsApp itself is the requirement, not just a messaging transport. All API
    specifics stay in this one adapter (see ADR 0013).
    """

    def send(self, *, recipient, subject: str, body: str, context: dict) -> None:
        if recipient is None or not getattr(recipient, "phone_number", ""):
            raise ValueError("Recipient has no phone number to send a WhatsApp message to.")
        if not settings.WHATSAPP_API_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
            raise RuntimeError("WhatsApp Business API is not configured.")

        response = requests.post(
            f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
            headers={"Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": recipient.phone_number,
                "type": "text",
                "text": {"body": body},
            },
            timeout=10,
        )
        response.raise_for_status()


def get_adapter(channel: str) -> NotificationAdapter:
    if channel == CHANNEL_EMAIL:
        return EmailNotificationAdapter()
    if channel == CHANNEL_PUSH:
        return WebPushNotificationAdapter()
    if channel == CHANNEL_WHATSAPP:
        return WhatsAppNotificationAdapter()
    return NoopNotificationAdapter()
