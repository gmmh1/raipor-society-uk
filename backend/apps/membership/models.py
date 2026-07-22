from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.membership.domain.guardian import RELATIONSHIP_CHOICES
from apps.membership.domain.status import STATUS_CHOICES, STATUS_PENDING


class MembershipTier(UUIDModel, TimeStampedModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    price_minor = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=8, default="GBP")
    billing_period_days = models.PositiveIntegerField(default=365)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "membership_tier"
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code}: {self.name}"


class Membership(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membership",
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    tier = models.ForeignKey(
        MembershipTier,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memberships",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "membership_membership"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["expires_at"]),
        ]


class GuardianRelationship(UUIDModel, TimeStampedModel):
    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guardian_relationships_as_guardian",
    )
    child = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guardian_relationships_as_child",
    )
    relationship_type = models.CharField(max_length=32, choices=RELATIONSHIP_CHOICES)
    consent_given_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "membership_guardian_relationship"
        constraints = [
            models.UniqueConstraint(fields=["guardian", "child"], name="uniq_guardian_child"),
        ]
        indexes = [
            models.Index(fields=["child"]),
            models.Index(fields=["guardian"]),
        ]

    def __str__(self) -> str:
        return f"{self.guardian_id} guardian of {self.child_id}"


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
