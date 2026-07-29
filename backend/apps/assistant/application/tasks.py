from celery import shared_task

from apps.assistant.application.indexing_service import reindex_document_version
from apps.documents.models import DocumentVersion


@shared_task
def index_document_version_task(version_id: str) -> int:
    try:
        version = DocumentVersion.objects.get(id=version_id)
    except DocumentVersion.DoesNotExist:
        return 0
    return reindex_document_version(version=version)
