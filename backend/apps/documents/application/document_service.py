import hashlib

from django.db import transaction
from django.db.models import Q, QuerySet

from apps.common.audit import record_audit_event
from apps.documents.domain.types import STAFF_ROLES, VISIBILITY_MEMBER, VISIBILITY_PUBLIC
from apps.documents.infrastructure import storage
from apps.documents.models import Document, DocumentVersion
from apps.identity.application.rbac_service import user_has_any_role


class DocumentError(ValueError):
    pass


def visible_documents_queryset(user) -> QuerySet[Document]:
    base = Document.objects.select_related("owner")
    if not user or not user.is_authenticated:
        return base.filter(visibility=VISIBILITY_PUBLIC)
    if user_has_any_role(user, STAFF_ROLES):
        return base
    return base.filter(visibility__in=[VISIBILITY_PUBLIC, VISIBILITY_MEMBER])


def get_visible_document(*, user, document_id) -> Document | None:
    return visible_documents_queryset(user).filter(id=document_id).first()


def search_documents(*, user, query: str = "") -> QuerySet[Document]:
    qs = visible_documents_queryset(user)
    query = (query or "").strip()
    if not query:
        return qs.order_by("-created_at")
    return (
        qs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(versions__extracted_text__icontains=query)
        )
        .distinct()
        .order_by("-created_at")
    )


@transaction.atomic
def create_document(
    *, owner, title: str, description: str, category: str, visibility: str
) -> Document:
    if not title.strip():
        raise DocumentError("Title is required.")

    document = Document.objects.create(
        title=title.strip(),
        description=description,
        category=category,
        visibility=visibility,
        owner=owner,
    )
    record_audit_event(
        actor=owner, action="document.created", entity=document, after={"title": document.title}
    )
    return document


@transaction.atomic
def create_version(
    *,
    document: Document,
    uploaded_by,
    original_filename: str,
    content_type: str,
    data: bytes,
) -> DocumentVersion:
    if not data:
        raise DocumentError("Uploaded file is empty.")

    next_version_number = (
        DocumentVersion.objects.select_for_update()
        .filter(document=document)
        .order_by("-version_number")
        .values_list("version_number", flat=True)
        .first()
        or 0
    ) + 1

    checksum = hashlib.sha256(data).hexdigest()
    file_key = f"documents/{document.id}/v{next_version_number}/{original_filename}"

    storage.upload_bytes(key=file_key, data=data, content_type=content_type)

    version = DocumentVersion.objects.create(
        document=document,
        version_number=next_version_number,
        file_key=file_key,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=len(data),
        checksum_sha256=checksum,
        uploaded_by=uploaded_by,
    )
    record_audit_event(
        actor=uploaded_by,
        action="document.version_uploaded",
        entity=version,
        after={"document_id": str(document.id), "version_number": next_version_number},
    )

    from apps.documents.application.tasks import extract_document_version_task

    transaction.on_commit(lambda: extract_document_version_task.delay(str(version.id)))
    return version


@transaction.atomic
def archive_document(*, document: Document, actor) -> Document:
    document.delete()  # SoftDeleteModel.delete() sets deleted_at, preserves the row
    record_audit_event(actor=actor, action="document.archived", entity=document)
    return document


def get_download_url(*, version: DocumentVersion) -> str:
    return storage.generate_presigned_download_url(key=version.file_key)
