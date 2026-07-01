from django.db import transaction
from django.utils import timezone

from apps.notifications.domain.types import STATUS_FAILED, STATUS_QUEUED, STATUS_SENT
from apps.notifications.infrastructure.adapters import get_adapter
from apps.notifications.models import Notification


@transaction.atomic
def queue_notification(
    *,
    recipient,
    channel: str,
    body: str,
    subject: str = "",
    context: dict | None = None,
) -> Notification:
    return Notification.objects.create(
        recipient=recipient,
        channel=channel,
        subject=subject,
        body=body,
        context=context or {},
        status=STATUS_QUEUED,
    )


@transaction.atomic
def dispatch_notification(notification: Notification) -> Notification:
    adapter = get_adapter(notification.channel)
    try:
        adapter.send(
            recipient=notification.recipient,
            subject=notification.subject,
            body=notification.body,
            context=notification.context,
        )
        notification.status = STATUS_SENT
        notification.sent_at = timezone.now()
        notification.error_message = ""
    except Exception as exc:  # noqa: BLE001
        notification.status = STATUS_FAILED
        notification.error_message = str(exc)

    notification.save(update_fields=["status", "sent_at", "error_message", "updated_at"])
    return notification
