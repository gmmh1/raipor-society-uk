from apps.notifications.application.dispatch_service import queue_notification
from apps.notifications.tasks import dispatch_notification_task


def enqueue_notification(*, recipient, channel: str, body: str, subject: str = "", context: dict | None = None):
    notification = queue_notification(
        recipient=recipient,
        channel=channel,
        subject=subject,
        body=body,
        context=context,
    )
    dispatch_notification_task.delay(str(notification.id))
    return notification
