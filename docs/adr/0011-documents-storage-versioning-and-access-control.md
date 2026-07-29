# ADR 0011: Documents Storage, Versioning, and Access Control

## Status

Accepted

## Context

Module 8 (Documents) is next in the build order. It must provide document upload,
versioning, and search, gated by access control, and produce extracted text so a later
module (Module 9, AI Knowledge Assistant) can chunk and embed that text into pgvector
without re-deriving it. Per the AI rules in `CLAUDE.md`, the RAG pipeline is
`Document -> Extraction -> Chunking -> Embedding -> pgvector -> Retrieval -> LLM -> Answer
with citations`; this ADR only covers the first stage (Document -> Extraction). Chunking,
embedding, and retrieval are out of scope here and belong to the AI Assistant module.

Object storage is MinIO (S3-compatible), already provisioned in `docker-compose.yml` with
`S3_ENDPOINT` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` / `S3_BUCKET` / `S3_REGION` in
`.env.example`, but nothing in the backend used it yet.

## Decision

Implement a `apps.documents` bounded context:

- `Document`: metadata entity (title, description, category, `visibility`, owner). Uses
  `UUIDModel`, `TimeStampedModel`, `SoftDeleteModel` so archiving a document preserves
  history instead of deleting rows.
- `DocumentVersion`: one immutable upload per version number (`document`, `version_number`,
  storage `file_key`, original filename, content type, size, SHA-256 checksum, uploader,
  `extraction_status`, `extracted_text`). Versions are never mutated after creation; a new
  upload always creates a new version rather than overwriting one, so past citations/links
  stay valid.

Storage abstraction (`apps.documents.infrastructure.storage`): a thin function-based wrapper
around `boto3`'s S3 client, configured from `S3_*` env vars against the MinIO endpoint. All
vendor-specific (AWS SDK) code is isolated to this one module — swapping MinIO for another
S3-compatible provider, or a different backend entirely, only touches this file. Nothing
elsewhere in the app imports `boto3` directly.

Extraction abstraction (`apps.documents.infrastructure.extraction`): synchronous, in-process
text extraction dispatched by content type:

- `text/plain` and `text/markdown`: decode directly.
- `application/pdf`: extract the embedded text layer via `pypdf` (pure Python, no native
  dependency).
- image types (`image/png`, `image/jpeg`, `image/tiff`): OCR via `pytesseract` against the
  system `tesseract-ocr` binary (added to the Docker image), per `CLAUDE.md`'s preference
  for Tesseract OCR.

Extraction runs as a Celery task (`extract_document_version_task`) queued immediately after
a version is uploaded, so large files never block the upload request. Failure sets
`extraction_status="failed"` with the error recorded, rather than blocking the upload itself
— a document with unextracted text is still downloadable and listed, just not yet
full-text-searchable.

Access control uses a three-tier `visibility` field rather than per-document ACLs, to match
the simplicity the existing role model already gives us:

- `public`: anyone, including anonymous users (e.g. published policies).
- `member`: any authenticated user.
- `staff`: only users holding `admin`, `volunteer`, or `treasurer` roles (reuses
  `apps.identity.application.rbac_service.user_has_any_role`, the same check every other
  module's role gates use).

Search (`search_documents`) filters the visibility-scoped queryset by `icontains` across
title, description, and any version's `extracted_text`. This is deliberately not a ranked
full-text or trigram index yet — see Future considerations.

APIs:

- `GET /api/documents/` — list/search (`?q=`), visibility-filtered.
- `POST /api/documents/` — create document metadata (staff only).
- `GET /api/documents/{id}/` — detail (visibility-checked).
- `POST /api/documents/{id}/versions/` — upload a new version file (staff only).
- `GET /api/documents/{id}/versions/{version_id}/download/` — presigned download URL
  (visibility-checked).
- `POST /api/documents/{id}/archive/` — soft-delete (staff only).

## Consequences

- Every document version is checksummed and immutable, giving a reliable audit trail for
  what was published when.
- Extraction is decoupled from upload, so it can be retried or re-run independently without
  re-uploading the file.
- The `extracted_text` column on `DocumentVersion` is exactly the input the AI Assistant
  module needs for chunking — no re-reading files from storage at RAG-index time.
- Storage is not vendor-locked: only `infrastructure/storage.py` speaks S3/boto3.

## Follow-up

- Scanned (image-only) PDFs are not OCR'd yet — only the embedded text layer is extracted.
  Rasterizing PDF pages for OCR needs Poppler/`pdf2image`, deferred until there's a real
  scanned-document use case.
- Search is `icontains`, not ranked. Add PostgreSQL trigram or full-text search (and later,
  pgvector semantic search once the AI Assistant module exists) when the document volume
  makes relevance ranking matter.
- No per-document custom ACLs (e.g. "only committee X") — the three-tier visibility model
  covers today's needs; revisit if a role/committee-scoped visibility requirement appears.
