from django.db import transaction

from apps.assistant.application.chunking_service import chunk_text
from apps.assistant.infrastructure.embeddings import generate_embedding
from apps.assistant.models import DocumentChunk
from apps.documents.domain.types import EXTRACTION_COMPLETED
from apps.documents.models import DocumentVersion


def reindex_document_version(*, version: DocumentVersion) -> int:
    """Delete and recreate all chunks for ``version``. Safe to call repeatedly."""
    if version.extraction_status != EXTRACTION_COMPLETED or not version.extracted_text:
        return 0

    chunks = chunk_text(version.extracted_text)
    embedded_chunks = [(content, generate_embedding(content)) for content in chunks]

    with transaction.atomic():
        DocumentChunk.objects.filter(document_version=version).delete()
        DocumentChunk.objects.bulk_create(
            DocumentChunk(
                document_version=version, chunk_index=index, content=content, embedding=embedding
            )
            for index, (content, embedding) in enumerate(embedded_chunks)
        )
    return len(embedded_chunks)
