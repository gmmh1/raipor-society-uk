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
            "image_url",
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


class MyEventRegistrationSerializer(EventRegistrationSerializer):
    event = EventSerializer(read_only=True)

    class Meta(EventRegistrationSerializer.Meta):
        fields = [*EventRegistrationSerializer.Meta.fields, "event"]


class EventRegistrationRequestSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()


class EventCheckInRequestSerializer(serializers.Serializer):
    registration_id = serializers.UUIDField(required=False)
    qr_token = serializers.UUIDField(required=False)

    def validate(self, attrs):
        has_registration_id = bool(attrs.get("registration_id"))
        has_qr_token = bool(attrs.get("qr_token"))
        if has_registration_id == has_qr_token:
            raise serializers.ValidationError(
                "Provide exactly one of registration_id or qr_token."
            )
        return attrs
