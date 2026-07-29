from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.common.models import TimeStampedModel, UUIDModel
from apps.notifications.domain.types import CHANNEL_CHOICES, STATUS_CHOICES, STATUS_QUEUED


class Notification(UUIDModel, TimeStampedModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    channel = models.CharField(max_length=32, choices=CHANNEL_CHOICES)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_QUEUED)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    dedup_key = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "notifications_notification"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["dedup_key"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["dedup_key"],
                condition=~Q(dedup_key=""),
                name="uniq_notification_dedup_key",
            ),
        ]


class PushSubscription(UUIDModel, TimeStampedModel):
    """A registered Web Push (VAPID) subscription for a user's browser/device.

    Web Push is a W3C standard with no vendor lock-in, unlike FCM/APNs, so it is the
    only "push" transport implemented today (see ADR 0013).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.URLField(max_length=1024, unique=True)
    p256dh_key = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notifications_push_subscription"
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]
