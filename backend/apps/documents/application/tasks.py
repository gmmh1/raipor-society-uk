from celery import shared_task

from apps.documents.domain.types import (
    EXTRACTION_COMPLETED,
    EXTRACTION_FAILED,
    EXTRACTION_UNSUPPORTED,
)
from apps.documents.infrastructure import extraction, storage
from apps.documents.models import DocumentVersion


@shared_task
def extract_document_version_task(version_id: str) -> None:
    try:
        version = DocumentVersion.objects.get(id=version_id)
    except DocumentVersion.DoesNotExist:
        return

    try:
        data = storage.download_bytes(key=version.file_key)
        text = extraction.extract_text(content_type=version.content_type, data=data)
    except extraction.UnsupportedContentTypeError:
        version.extraction_status = EXTRACTION_UNSUPPORTED
        version.save(update_fields=["extraction_status", "updated_at"])
        return
    except (storage.StorageError, extraction.ExtractionError) as exc:
        version.extraction_status = EXTRACTION_FAILED
        version.extraction_error = str(exc)
        version.save(update_fields=["extraction_status", "extraction_error", "updated_at"])
        return

    version.extraction_status = EXTRACTION_COMPLETED
    version.extracted_text = text
    version.save(update_fields=["extraction_status", "extracted_text", "updated_at"])

    from apps.assistant.application.tasks import index_document_version_task

    index_document_version_task.delay(str(version.id))
