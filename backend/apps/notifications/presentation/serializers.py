from rest_framework import serializers

from apps.notifications.domain.types import CHANNEL_CHOICES
from apps.notifications.models import Notification, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    recipient_id = serializers.UUIDField(source="recipient.id", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient_id",
            "channel",
            "subject",
            "body",
            "context",
            "status",
            "error_message",
            "sent_at",
            "created_at",
            "updated_at",
        ]


class SendNotificationSerializer(serializers.Serializer):
    recipient_id = serializers.UUIDField()
    channel = serializers.ChoiceField(choices=[choice[0] for choice in CHANNEL_CHOICES])
    subject = serializers.CharField(required=False, allow_blank=True, max_length=255)
    body = serializers.CharField(max_length=5000)
    context = serializers.JSONField(required=False)


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ["id", "endpoint", "is_active", "created_at"]


class RegisterPushSubscriptionRequestSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=1024)
    p256dh_key = serializers.CharField(max_length=255)
    auth_key = serializers.CharField(max_length=255)


class UnregisterPushSubscriptionRequestSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=1024)
