from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel
from apps.documents.domain.types import (
    CATEGORY_CHOICES,
    CATEGORY_OTHER,
    EXTRACTION_PENDING,
    EXTRACTION_STATUS_CHOICES,
    VISIBILITY_CHOICES,
    VISIBILITY_MEMBER,
)


class Document(UUIDModel, TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    visibility = models.CharField(
        max_length=16, choices=VISIBILITY_CHOICES, default=VISIBILITY_MEMBER
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_documents"
    )

    class Meta:
        db_table = "documents_document"
        indexes = [
            models.Index(fields=["visibility", "category"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class DocumentVersion(UUIDModel, TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    file_key = models.CharField(max_length=512)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=128)
    size_bytes = models.BigIntegerField()
    checksum_sha256 = models.CharField(max_length=64)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_document_versions",
    )
    extraction_status = models.CharField(
        max_length=16, choices=EXTRACTION_STATUS_CHOICES, default=EXTRACTION_PENDING
    )
    extracted_text = models.TextField(blank=True)
    extraction_error = models.TextField(blank=True)

    class Meta:
        db_table = "documents_document_version"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "version_number"], name="uniq_document_version_number"
            ),
        ]
        indexes = [
            models.Index(fields=["document", "-version_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_id} v{self.version_number}"
