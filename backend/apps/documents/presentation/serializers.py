from rest_framework import serializers

from apps.documents.domain.types import CATEGORY_CHOICES, VISIBILITY_CHOICES
from apps.documents.models import Document, DocumentVersion


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "version_number",
            "original_filename",
            "content_type",
            "size_bytes",
            "checksum_sha256",
            "extraction_status",
            "created_at",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)
    owner_id = serializers.UUIDField(source="owner.id", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "category",
            "visibility",
            "owner_id",
            "versions",
            "created_at",
            "updated_at",
        ]


class DocumentCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    category = serializers.ChoiceField(choices=[choice[0] for choice in CATEGORY_CHOICES])
    visibility = serializers.ChoiceField(choices=[choice[0] for choice in VISIBILITY_CHOICES])


class DocumentVersionUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class DocumentDownloadSerializer(serializers.Serializer):
    url = serializers.URLField()
