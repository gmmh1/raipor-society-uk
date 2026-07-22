from django.conf import settings
from django.core.mail import send_mail

from apps.notifications.domain.types import CHANNEL_EMAIL


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
            subject=subject or "Raipor Society UK",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )


def get_adapter(channel: str) -> NotificationAdapter:
    if channel == CHANNEL_EMAIL:
        return EmailNotificationAdapter()
    # Push and WhatsApp adapters are a follow-up phase; queued notifications on
    # those channels are accepted but not yet delivered.
    return NoopNotificationAdapter()
