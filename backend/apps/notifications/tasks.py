from celery import shared_task
from django.utils import timezone

from apps.notifications.application.dispatch_service import dispatch_notification
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.domain.types import CHANNEL_EMAIL
from apps.notifications.models import Notification


@shared_task
def enqueue_event_reminders_task() -> int:
    from datetime import timedelta

    from apps.events.domain.status import REG_STATUS_REGISTERED
    from apps.events.models import EventRegistration

    now = timezone.now()
    upcoming = now + timedelta(hours=24)
    registrations = EventRegistration.objects.filter(
        status=REG_STATUS_REGISTERED,
        event__starts_at__gte=now,
        event__starts_at__lte=upcoming,
    ).select_related("event", "user")

    count = 0
    for registration in registrations:
        enqueue_notification(
            recipient=registration.user,
            channel=CHANNEL_EMAIL,
            subject="Event reminder",
            body=f"Reminder: '{registration.event.title}' starts at {registration.event.starts_at}.",
            context={"event_id": str(registration.event.id), "registration_id": str(registration.id)},
        )
        count += 1
    return count


@shared_task
def enqueue_event_summary_task() -> int:
    from datetime import timedelta

    from apps.events.domain.status import REG_STATUS_ATTENDED
    from apps.events.models import EventRegistration

    cutoff = timezone.now() - timedelta(hours=24)
    attended = EventRegistration.objects.filter(
        status=REG_STATUS_ATTENDED,
        checked_in_at__gte=cutoff,
    ).select_related("event", "user")

    count = 0
    for registration in attended:
        enqueue_notification(
            recipient=registration.user,
            channel=CHANNEL_EMAIL,
            subject="Thanks for attending",
            body=f"Thanks for attending '{registration.event.title}'.",
            context={"event_id": str(registration.event.id), "registration_id": str(registration.id)},
        )
        count += 1
    return count


@shared_task
def dispatch_notification_task(notification_id: str) -> None:
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return

    dispatch_notification(notification)
