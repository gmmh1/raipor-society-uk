from rest_framework import serializers

from apps.membership.domain.guardian import RELATIONSHIP_CHOICES
from apps.membership.domain.status import STATUS_CHOICES
from apps.membership.models import GuardianRelationship, Membership, MembershipTier


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
    is_minor = serializers.BooleanField(source="user.is_minor", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user_id",
            "username",
            "email",
            "is_minor",
            "status",
            "tier",
            "started_at",
            "ended_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]


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
