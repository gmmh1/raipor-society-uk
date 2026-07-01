import uuid

from django.conf import settings
from django.db import models

from apps.membership.domain.status import STATUS_CHOICES, STATUS_PENDING


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membership",
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "membership_membership"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]


class MembershipStatusTransition(models.Model):
    id = models.BigAutoField(primary_key=True)
    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name="transitions",
    )
    from_status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    to_status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="membership_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "membership_status_transition"
        indexes = [
            models.Index(fields=["changed_at"]),
            models.Index(fields=["from_status", "to_status"]),
        ]
