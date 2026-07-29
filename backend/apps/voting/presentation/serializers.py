from rest_framework import serializers

from apps.voting.application.poll_service import has_user_voted, poll_status
from apps.voting.domain.types import VISIBILITY_CHOICES
from apps.voting.models import Poll, PollOption


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ["id", "text", "display_order"]


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            "id",
            "title",
            "description",
            "visibility",
            "opens_at",
            "closes_at",
            "quorum",
            "options",
            "status",
            "has_voted",
            "created_at",
        ]

    def get_status(self, obj) -> str:
        return poll_status(obj)

    def get_has_voted(self, obj) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return has_user_voted(poll=obj, user=user)


class PollCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    visibility = serializers.ChoiceField(choices=[choice[0] for choice in VISIBILITY_CHOICES])
    opens_at = serializers.DateTimeField()
    closes_at = serializers.DateTimeField()
    quorum = serializers.IntegerField(min_value=0, default=0)
    options = serializers.ListField(child=serializers.CharField(max_length=255), min_length=2)


class CastVoteRequestSerializer(serializers.Serializer):
    option_id = serializers.UUIDField()
