import uuid

from django.conf import settings
from django.db import models

from apps.notifications.domain.types import CHANNEL_CHOICES, STATUS_CHOICES, STATUS_QUEUED


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications_notification"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["channel"]),
        ]
