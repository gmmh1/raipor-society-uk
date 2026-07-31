from rest_framework import serializers

from apps.voting.application.poll_service import has_user_voted, poll_status
from apps.voting.domain.types import VISIBILITY_CHOICES
from apps.voting.models import Poll, PollOption


class PollOptionSerializer(serializers.ModelSerializer):
    candidate_id = serializers.UUIDField(source="candidate.id", read_only=True, allow_null=True)

    class Meta:
        model = PollOption
        fields = ["id", "text", "image_url", "display_order", "candidate_id"]


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
            "position",
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


class PollOptionInputSerializer(serializers.Serializer):
    # General polls: free text, no member link. Elections (poll.position set):
    # text/image_url are ignored server-side — candidate_user_id is required
    # instead, and the candidate's name/photo are derived from their own member
    # profile (see create_poll), never trusted from the client.
    text = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    image_url = serializers.URLField(required=False, allow_blank=True, default="")
    candidate_user_id = serializers.UUIDField(required=False)


class PollCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    position = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")
    visibility = serializers.ChoiceField(choices=[choice[0] for choice in VISIBILITY_CHOICES])
    opens_at = serializers.DateTimeField()
    closes_at = serializers.DateTimeField()
    quorum = serializers.IntegerField(min_value=0, default=0)
    # The real minimum (1 for an uncontested election, 2 for a general poll) is
    # enforced in create_poll(), which knows which kind this is; min_length=1 here
    # just rejects a completely empty list before that.
    options = PollOptionInputSerializer(many=True, min_length=1)


class CastVoteRequestSerializer(serializers.Serializer):
    option_id = serializers.UUIDField()
