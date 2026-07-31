from rest_framework import serializers

from apps.chat.domain.types import MAX_MESSAGE_LENGTH
from apps.chat.models import ChatChannel, ChatMessage


class ChatChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatChannel
        fields = ["id", "name", "channel_type", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.UUIDField(source="sender.id", read_only=True, allow_null=True)
    sender_username = serializers.CharField(
        source="sender.username", read_only=True, allow_null=True
    )

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "channel_id",
            "sender_id",
            "sender_username",
            "content",
            "is_flagged",
            "created_at",
        ]


class CreateDirectChannelRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


class CreateGroupChannelRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    member_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class AddMemberRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


class SendMessageRequestSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=MAX_MESSAGE_LENGTH)


class FlagMessageRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class VideoCallTokenSerializer(serializers.Serializer):
    domain = serializers.CharField()
    room = serializers.CharField()
    token = serializers.CharField()
