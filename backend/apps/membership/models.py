from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel
from apps.membership.domain.guardian import RELATIONSHIP_CHOICES
from apps.membership.domain.position import COMMITTEE_POSITION_CHOICES
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


class MemberProfile(UUIDModel, TimeStampedModel):
    """Public-facing profile info for the About Us page — separate from Membership
    (billing/status lifecycle) and from User (auth). Committee position no longer
    lives here — see ``Committee``/``CommitteeMembership`` — since a position is
    scoped to a specific committee term, not a permanent attribute of a member.
    Everything on this model is the member's own, opt-in choice via
    ``public_consent``."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    public_consent = models.BooleanField(default=False)

    class Meta:
        db_table = "membership_member_profile"
        indexes = [
            models.Index(fields=["public_consent"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} profile"


class Committee(UUIDModel, TimeStampedModel, SoftDeleteModel):
    """A dated committee term (e.g. "2024–2026 Committee"). Exactly one committee
    is "current" at a time — the one whose date range covers today (see
    ``committee_service.current_committee``) — and once its ``ends_at`` passes, it
    automatically becomes a past committee with no extra bookkeeping: "current" is
    a live date comparison, not a flag admins have to remember to flip.
    """

    name = models.CharField(max_length=255)
    starts_at = models.DateField()
    ends_at = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="committees_created",
    )

    class Meta:
        db_table = "membership_committee"
        ordering = ("-starts_at",)
        indexes = [
            models.Index(fields=["starts_at", "ends_at"]),
        ]

    def __str__(self) -> str:
        return self.name


class CommitteeMembership(UUIDModel, TimeStampedModel):
    """One member's position within one committee term. A member can hold at most
    one position per committee (unique_together below), but the same member can
    appear across many committees over the years — that history is exactly what
    makes past committees meaningful to browse from the timeline."""

    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="committee_memberships"
    )
    position = models.CharField(max_length=128, choices=[(name, name) for name in COMMITTEE_POSITION_CHOICES])
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "membership_committee_membership"
        constraints = [
            models.UniqueConstraint(fields=["committee", "user"], name="uniq_committee_member"),
        ]
        indexes = [
            models.Index(fields=["committee", "display_order"]),
        ]
        ordering = ("display_order",)

    def __str__(self) -> str:
        return f"{self.user_id}: {self.position} ({self.committee_id})"
