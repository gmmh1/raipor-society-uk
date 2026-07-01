from django.db import transaction
from django.utils import timezone

from apps.events.domain.status import REG_STATUS_ATTENDED, REG_STATUS_REGISTERED
from apps.events.models import Event, EventRegistration
from apps.membership.domain.status import STATUS_ACTIVE
from apps.membership.models import Membership


class EventServiceError(ValueError):
    pass


@transaction.atomic
def register_for_event(event: Event, user) -> EventRegistration:
    if not event.is_published:
        raise EventServiceError("This event is not open for registration.")

    if event.capacity > 0:
        active_count = EventRegistration.objects.filter(
            event=event,
            status=REG_STATUS_REGISTERED,
        ).count()
        if active_count >= event.capacity:
            raise EventServiceError("Event registration capacity has been reached.")

    try:
        membership = Membership.objects.get(user=user)
    except Membership.DoesNotExist as exc:
        raise EventServiceError("Only active members can register for events.") from exc

    if membership.status != STATUS_ACTIVE:
        raise EventServiceError("Only active members can register for events.")

    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        user=user,
        defaults={"status": REG_STATUS_REGISTERED},
    )
    if not created and registration.status == REG_STATUS_REGISTERED:
        raise EventServiceError("You are already registered for this event.")

    if not created and registration.status != REG_STATUS_REGISTERED:
        registration.status = REG_STATUS_REGISTERED
        registration.checked_in_at = None
        registration.checked_in_by = None
        registration.save(update_fields=["status", "checked_in_at", "checked_in_by", "updated_at"])

    return registration


@transaction.atomic
def check_in_registration(registration: EventRegistration, actor) -> EventRegistration:
    if registration.status != REG_STATUS_REGISTERED:
        raise EventServiceError("Only registered attendees can be checked in.")

    registration.status = REG_STATUS_ATTENDED
    registration.checked_in_at = timezone.now()
    registration.checked_in_by = actor
    registration.save(update_fields=["status", "checked_in_at", "checked_in_by", "updated_at"])
    return registration
