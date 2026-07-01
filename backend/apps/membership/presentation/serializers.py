from rest_framework import serializers

from apps.membership.domain.status import STATUS_CHOICES
from apps.membership.models import Membership


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = [
            "id",
            "status",
            "started_at",
            "ended_at",
            "created_at",
            "updated_at",
        ]


class MembershipTransitionSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    to_status = serializers.ChoiceField(choices=[choice[0] for choice in STATUS_CHOICES])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=2000)
