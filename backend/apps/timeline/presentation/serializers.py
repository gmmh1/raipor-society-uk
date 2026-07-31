from rest_framework import serializers

from apps.timeline.models import TimelineEntry


class TimelineEntrySerializer(serializers.ModelSerializer):
    committee_id = serializers.UUIDField(read_only=True, allow_null=True)

    class Meta:
        model = TimelineEntry
        fields = [
            "id",
            "title",
            "description",
            "entry_date",
            "end_date",
            "image_url",
            "is_published",
            "committee_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TimelineEntryCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    entry_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True, default=None)
    image_url = serializers.URLField(required=False, allow_blank=True, default="")
    is_published = serializers.BooleanField(required=False, default=True)
