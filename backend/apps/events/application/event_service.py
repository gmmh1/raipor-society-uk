from django.db import transaction
from django.utils import timezone

from apps.common.audit import record_audit_event
from apps.events.domain.status import (
    REG_STATUS_ATTENDED,
    REG_STATUS_CANCELLED,
    REG_STATUS_REGISTERED,
    REG_STATUS_WAITLISTED,
)
from apps.events.models import Event, EventRegistration
from apps.identity.application.rbac_service import user_has_any_role
from apps.membership.domain.status import STATUS_ACTIVE
from apps.membership.models import Membership
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.domain.types import CHANNEL_EMAIL

ACTIVE_REGISTRATION_STATUSES = (REG_STATUS_REGISTERED, REG_STATUS_WAITLISTED)


class EventServiceError(ValueError):
    pass


@transaction.atomic
def register_for_event(event: Event, user) -> EventRegistration:
    if not event.is_published:
        raise EventServiceError("This event is not open for registration.")

    try:
        membership = Membership.objects.get(user=user)
    except Membership.DoesNotExist as exc:
        raise EventServiceError("Only active members can register for events.") from exc

    if membership.status != STATUS_ACTIVE:
        raise EventServiceError("Only active members can register for events.")

    target_status = REG_STATUS_REGISTERED
    if event.capacity > 0:
        confirmed_count = EventRegistration.objects.filter(
            event=event,
            status=REG_STATUS_REGISTERED,
        ).count()
        if confirmed_count >= event.capacity:
            target_status = REG_STATUS_WAITLISTED

    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        user=user,
        defaults={"status": target_status},
    )
    if not created and registration.status in ACTIVE_REGISTRATION_STATUSES:
        raise EventServiceError("You are already registered for this event.")

    if not created and registration.status not in ACTIVE_REGISTRATION_STATUSES:
        registration.status = target_status
        registration.checked_in_at = None
        registration.checked_in_by = None
        registration.save(update_fields=["status", "checked_in_at", "checked_in_by", "updated_at"])

    if target_status == REG_STATUS_WAITLISTED:
        subject = "Added to event waitlist"
        body = f"You have been added to the waitlist for '{event.title}'."
    else:
        subject = "Event registration confirmed"
        body = f"You are registered for '{event.title}'."

    enqueue_notification(
        recipient=user,
        channel=CHANNEL_EMAIL,
        subject=subject,
        body=body,
        context={"event_id": str(event.id), "registration_id": str(registration.id)},
    )

    return registration


@transaction.atomic
def cancel_registration(registration: EventRegistration, actor) -> EventRegistration:
    if registration.status not in ACTIVE_REGISTRATION_STATUSES:
        raise EventServiceError("Only registered or waitlisted attendees can be cancelled.")

    if actor.pk != registration.user_id and not user_has_any_role(actor, ("admin", "volunteer")):
        raise EventServiceError("You are not authorized to cancel this registration.")

    was_confirmed = registration.status == REG_STATUS_REGISTERED

    registration.status = REG_STATUS_CANCELLED
    registration.save(update_fields=["status", "updated_at"])

    enqueue_notification(
        recipient=registration.user,
        channel=CHANNEL_EMAIL,
        subject="Event registration cancelled",
        body=f"Your registration for '{registration.event.title}' has been cancelled.",
        context={"event_id": str(registration.event_id), "registration_id": str(registration.id)},
    )

    if was_confirmed:
        promoted = (
            EventRegistration.objects.select_for_update()
            .filter(event=registration.event, status=REG_STATUS_WAITLISTED)
            .order_by("created_at")
            .first()
        )
        if promoted is not None:
            promoted.status = REG_STATUS_REGISTERED
            promoted.save(update_fields=["status", "updated_at"])
            enqueue_notification(
                recipient=promoted.user,
                channel=CHANNEL_EMAIL,
                subject="Event registration confirmed",
                body=f"A spot opened up: you are now registered for '{registration.event.title}'.",
                context={
                    "event_id": str(registration.event_id),
                    "registration_id": str(promoted.id),
                },
            )

    return registration


@transaction.atomic
def check_in_registration(registration: EventRegistration, actor) -> EventRegistration:
    if registration.status != REG_STATUS_REGISTERED:
        raise EventServiceError("Only registered attendees can be checked in.")

    registration.status = REG_STATUS_ATTENDED
    registration.checked_in_at = timezone.now()
    registration.checked_in_by = actor
    registration.save(update_fields=["status", "checked_in_at", "checked_in_by", "updated_at"])

    enqueue_notification(
        recipient=registration.user,
        channel=CHANNEL_EMAIL,
        subject="Event check-in completed",
        body=f"You have been checked in for '{registration.event.title}'.",
        context={"registration_id": str(registration.id), "event_id": str(registration.event.id)},
    )
    return registration


@transaction.atomic
def cancel_event(event: Event, actor) -> Event:
    """Soft-delete an event. Historical EventRegistration rows are preserved."""
    if not event.is_published:
        raise EventServiceError("Event is already unpublished.")

    event.is_published = False
    event.save(update_fields=["is_published", "updated_at"])
    event.delete()  # SoftDeleteModel.delete() sets deleted_at, does not remove the row

    record_audit_event(actor=actor, action="event.cancelled", entity=event)

    for registration in event.registrations.filter(status=REG_STATUS_REGISTERED):
        enqueue_notification(
            recipient=registration.user,
            channel=CHANNEL_EMAIL,
            subject="Event cancelled",
            body=f"'{event.title}' has been cancelled.",
            context={"event_id": str(event.id)},
        )

    return event
