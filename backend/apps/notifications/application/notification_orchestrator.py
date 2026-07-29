from apps.notifications.application.dispatch_service import queue_notification
from apps.notifications.domain.types import STATUS_QUEUED
from apps.notifications.tasks import dispatch_notification_task


def enqueue_notification(
    *,
    recipient,
    channel: str,
    body: str,
    subject: str = "",
    context: dict | None = None,
    dedup_key: str = "",
):
    notification = queue_notification(
        recipient=recipient,
        channel=channel,
        subject=subject,
        body=body,
        context=context,
        dedup_key=dedup_key,
    )
    if notification.status == STATUS_QUEUED:
        dispatch_notification_task.delay(str(notification.id))
    return notification
