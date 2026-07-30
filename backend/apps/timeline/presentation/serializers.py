from rest_framework import serializers

from apps.timeline.models import TimelineEntry


class TimelineEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEntry
        fields = [
            "id",
            "title",
            "description",
            "entry_date",
            "image_url",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimelineEntryCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    entry_date = serializers.DateField()
    image_url = serializers.URLField(required=False, allow_blank=True, default="")
    is_published = serializers.BooleanField(required=False, default=True)
