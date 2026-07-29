from django.core.management.base import BaseCommand

from apps.assistant.application.indexing_service import reindex_document_version
from apps.documents.domain.types import EXTRACTION_COMPLETED
from apps.documents.models import DocumentVersion


class Command(BaseCommand):
    help = (
        "Re-index all document versions with completed text extraction "
        "into the assistant's vector store."
    )

    def handle(self, *args, **options):
        versions = DocumentVersion.objects.filter(extraction_status=EXTRACTION_COMPLETED)
        total_chunks = 0
        for version in versions:
            count = reindex_document_version(version=version)
            total_chunks += count
            self.stdout.write(f"Indexed {version.id}: {count} chunks")

        self.stdout.write(
            self.style.SUCCESS(
                f"Re-indexed {versions.count()} versions, {total_chunks} chunks total."
            )
        )
