from rest_framework import serializers

from apps.membership.application.committee_service import current_committee
from apps.membership.domain.guardian import RELATIONSHIP_CHOICES
from apps.membership.domain.position import COMMITTEE_POSITION_CHOICES
from apps.membership.domain.status import STATUS_CHOICES
from apps.membership.models import (
    Committee,
    CommitteeMembership,
    GuardianRelationship,
    MemberProfile,
    Membership,
    MembershipTier,
)


class MembershipSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source="tier.code", read_only=True, allow_null=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "status",
            "tier",
            "started_at",
            "ended_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]


class MembershipAdminSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source="tier.code", read_only=True, allow_null=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    is_minor = serializers.BooleanField(source="user.is_minor", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            "id",
            "user_id",
            "username",
            "email",
            "phone_number",
            "avatar_url",
            "is_minor",
            "is_active",
            "status",
            "tier",
            "started_at",
            "ended_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]

    def get_avatar_url(self, membership: Membership) -> str:
        return getattr(getattr(membership.user, "profile", None), "avatar_url", "") or ""


class MembershipTransitionSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    to_status = serializers.ChoiceField(choices=[choice[0] for choice in STATUS_CHOICES])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class GuardianRelationshipSerializer(serializers.ModelSerializer):
    guardian_id = serializers.UUIDField(source="guardian.id", read_only=True)
    guardian_username = serializers.CharField(source="guardian.username", read_only=True)
    child_id = serializers.UUIDField(source="child.id", read_only=True)
    child_username = serializers.CharField(source="child.username", read_only=True)

    class Meta:
        model = GuardianRelationship
        fields = [
            "id",
            "guardian_id",
            "guardian_username",
            "child_id",
            "child_username",
            "relationship_type",
            "consent_given_at",
            "created_at",
        ]


class GuardianLinkRequestSerializer(serializers.Serializer):
    guardian_id = serializers.UUIDField()
    child_id = serializers.UUIDField()
    relationship_type = serializers.ChoiceField(
        choices=[choice[0] for choice in RELATIONSHIP_CHOICES]
    )


class GuardianConsentRequestSerializer(serializers.Serializer):
    relationship_id = serializers.UUIDField()


class MembershipTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipTier
        fields = [
            "id",
            "code",
            "name",
            "price_minor",
            "currency",
            "billing_period_days",
            "is_active",
        ]


class TierAssignmentRequestSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    tier_code = serializers.CharField(max_length=64)


class DuesRecordRequestSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    reference = serializers.CharField(required=False, allow_blank=True, max_length=128)


class MyProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    position = serializers.SerializerMethodField()

    class Meta:
        model = MemberProfile
        fields = ["position", "avatar_url", "bio", "public_consent", "phone_number"]

    def get_position(self, profile: MemberProfile) -> str:
        committee = current_committee()
        if committee is None:
            return ""
        membership = CommitteeMembership.objects.filter(committee=committee, user=profile.user).first()
        return membership.position if membership else ""


class ProfileUpdateRequestSerializer(serializers.Serializer):
    avatar_url = serializers.URLField(required=False, allow_blank=True, default="")
    bio = serializers.CharField(required=False, allow_blank=True, max_length=2000, default="")
    public_consent = serializers.BooleanField(required=False, default=False)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=32, default="")


class CommitteeSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = Committee
        fields = ["id", "name", "starts_at", "ends_at", "is_current", "created_at"]

    def get_is_current(self, committee: Committee) -> bool:
        current = self.context.get("current_committee_id")
        if current is None:
            current = getattr(current_committee(), "id", None)
        return committee.id == current


class CommitteeCreateRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    starts_at = serializers.DateField()
    ends_at = serializers.DateField(required=False, allow_null=True, default=None)


class CommitteeMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = CommitteeMembership
        fields = ["user_id", "name", "avatar_url", "position", "display_order"]

    def get_name(self, membership: CommitteeMembership) -> str:
        user = membership.user
        return (f"{user.first_name} {user.last_name}".strip()) or user.username

    def get_avatar_url(self, membership: CommitteeMembership) -> str:
        return getattr(getattr(membership.user, "profile", None), "avatar_url", "") or ""


class SetCommitteeMemberRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    position = serializers.ChoiceField(choices=COMMITTEE_POSITION_CHOICES)


class AdminCreateMemberRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    date_of_birth = serializers.DateField()
    phone_number = serializers.CharField(max_length=32)

    def validate_phone_number(self, value: str) -> str:
        digits = sum(character.isdigit() for character in value)
        if digits < 7:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value


class AdminUpdateContactRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    phone_number = serializers.CharField(required=False, max_length=32)
    avatar_url = serializers.URLField(required=False)

    def validate_phone_number(self, value: str) -> str:
        digits = sum(character.isdigit() for character in value)
        if digits < 7:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Provide at least a phone number or a photo.")
        return attrs


class AdminSetActiveRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    is_active = serializers.BooleanField()


class AdminEraseMemberRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


class PublicProfileSerializer(serializers.ModelSerializer):
    """Used for both the current-committee roster and the plain-members list on
    the public About Us page. ``position`` comes from ``context["memberships_by_user_id"]``
    (a committee's CommitteeMembership rows keyed by user id) rather than the model
    directly — a profile has no position of its own now, only within a committee."""

    user_id = serializers.UUIDField(source="user.id", read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    position = serializers.SerializerMethodField()
    display_order = serializers.SerializerMethodField()

    class Meta:
        model = MemberProfile
        fields = ["user_id", "name", "position", "display_order", "avatar_url", "bio", "email", "phone_number"]

    def get_name(self, profile: MemberProfile) -> str:
        user = profile.user
        return (f"{user.first_name} {user.last_name}".strip()) or user.username

    def get_position(self, profile: MemberProfile) -> str:
        membership = self._membership_for(profile)
        return membership.position if membership else ""

    def get_display_order(self, profile: MemberProfile) -> int:
        membership = self._membership_for(profile)
        return membership.display_order if membership else 0

    def _membership_for(self, profile: MemberProfile):
        memberships_by_user_id = self.context.get("memberships_by_user_id", {})
        return memberships_by_user_id.get(profile.user_id)
