from rest_framework import serializers

from apps.events.models import Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "starts_at",
            "ends_at",
            "location",
            "capacity",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if attrs["ends_at"] <= attrs["starts_at"]:
            raise serializers.ValidationError("Event end time must be after start time.")
        return attrs


class EventRegistrationSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(source="event.id", read_only=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "event_id",
            "user_id",
            "status",
            "qr_token",
            "checked_in_at",
            "created_at",
            "updated_at",
        ]


class EventRegistrationRequestSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()


class EventCheckInRequestSerializer(serializers.Serializer):
    registration_id = serializers.UUIDField()
