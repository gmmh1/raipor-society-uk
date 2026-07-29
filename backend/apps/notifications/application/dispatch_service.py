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
    dedup_key: str = "",
) -> Notification:
    if dedup_key:
        existing = Notification.objects.filter(
            dedup_key=dedup_key, status__in=[STATUS_QUEUED, STATUS_SENT]
        ).first()
        if existing is not None:
            return existing

    return Notification.objects.create(
        recipient=recipient,
        channel=channel,
        subject=subject,
        body=body,
        context=context or {},
        status=STATUS_QUEUED,
        dedup_key=dedup_key,
    )


def dispatch_notification(notification: Notification) -> Notification:
    """Attempt delivery once. Raises on failure so the caller (the Celery task) can retry.

    ``status``/``error_message`` reflect the outcome of this attempt regardless of
    whether it's retried again later, so a notification stuck retrying is still
    observable via the admin/API rather than silently pending. Deliberately not
    wrapped in ``@transaction.atomic``: the failure-branch ``save()`` must persist
    even though this function re-raises immediately afterward, and an atomic block
    would roll that save back along with the exception.
    """
    adapter = get_adapter(notification.channel)
    notification.attempts += 1
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
        notification.save(
            update_fields=["status", "sent_at", "error_message", "attempts", "updated_at"]
        )
    except Exception as exc:  # noqa: BLE001
        notification.status = STATUS_FAILED
        notification.error_message = str(exc)
        notification.save(update_fields=["status", "error_message", "attempts", "updated_at"])
        raise

    return notification
