from django.conf import settings
from django.db import models
from pgvector.django import VectorField

from apps.assistant.domain.types import EMBEDDING_DIMENSIONS
from apps.common.models import TimeStampedModel, UUIDModel
from apps.documents.models import DocumentVersion


class DocumentChunk(UUIDModel, TimeStampedModel):
    document_version = models.ForeignKey(
        DocumentVersion, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)

    class Meta:
        db_table = "assistant_document_chunk"
        constraints = [
            models.UniqueConstraint(
                fields=["document_version", "chunk_index"], name="uniq_chunk_index_per_version"
            ),
        ]
        indexes = [
            models.Index(fields=["document_version"]),
        ]

    def __str__(self) -> str:
        return f"{self.document_version_id} chunk {self.chunk_index}"


class AssistantInteraction(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="assistant_interactions",
    )
    question = models.TextField()
    answer = models.TextField()
    citations = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "assistant_interaction"
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.question[:50]}"
