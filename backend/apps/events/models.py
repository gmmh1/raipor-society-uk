import uuid

from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel
from apps.events.domain.status import REG_STATUS_REGISTERED, REGISTRATION_STATUS_CHOICES


class Event(UUIDModel, TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_created",
    )

    class Meta:
        db_table = "events_event"
        indexes = [
            models.Index(fields=["is_published", "starts_at"]),
            models.Index(fields=["created_at"]),
        ]


class EventRegistration(UUIDModel, TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_registrations",
    )
    status = models.CharField(
        max_length=32,
        choices=REGISTRATION_STATUS_CHOICES,
        default=REG_STATUS_REGISTERED,
    )
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="event_checkins_recorded",
    )

    class Meta:
        db_table = "events_registration"
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_event_user_registration"),
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]
