from pgvector.django import CosineDistance

from apps.assistant.domain.types import DEFAULT_TOP_K
from apps.assistant.infrastructure.embeddings import generate_embedding
from apps.assistant.models import DocumentChunk
from apps.documents.application.document_service import visible_documents_queryset


def search_relevant_chunks(
    *, user, question: str, top_k: int = DEFAULT_TOP_K
) -> list[DocumentChunk]:
    query_embedding = generate_embedding(question)
    visible_document_ids = visible_documents_queryset(user).values_list("id", flat=True)

    return list(
        DocumentChunk.objects.filter(document_version__document__in=visible_document_ids)
        .select_related("document_version", "document_version__document")
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:top_k]
    )
