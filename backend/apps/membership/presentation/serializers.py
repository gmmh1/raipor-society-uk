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


class MembershipTransitionSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    to_status = serializers.ChoiceField(choices=[choice[0] for choice in STATUS_CHOICES])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class GuardianRelationshipSerializer(serializers.ModelSerializer):
    guardian_id = serializers.UUIDField(source="guardian.id", read_only=True)
    child_id = serializers.UUIDField(source="child.id", read_only=True)

    class Meta:
        model = GuardianRelationship
        fields = [
            "id",
            "guardian_id",
            "child_id",
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
