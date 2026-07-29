# ADR 0012: AI Knowledge Assistant RAG Pipeline

## Status

Accepted

## Context

Module 9 (AI Knowledge Assistant) is next in the build order, following Module 8
(Documents, ADR 0011) which already produces `DocumentVersion.extracted_text`. Per the
AI rules in `CLAUDE.md`, the pipeline is fixed: `Document -> Extraction -> Chunking ->
Embedding -> pgvector -> Retrieval -> LLM -> Answer with citations`, the assistant must
never answer from memory alone, and it must respect user permissions. Extraction is
already done (Module 8); this ADR covers Chunking through Answer.

The stack is already committed to Ollama (`qwen2.5:3b-instruct`) for generation and a
BAAI BGE model for embeddings, both reachable at `OLLAMA_BASE_URL` (already provisioned
as a service in `docker-compose.yml`, env vars already in `.env.example`). Postgres runs
the `pgvector/pgvector:pg16` image, but nothing in the backend used the `vector` extension
or type yet.

## Decision

New bounded context `apps.assistant`:

- `DocumentChunk`: one row per chunk of a `DocumentVersion`'s extracted text —
  `document_version` (FK, cascade), `chunk_index`, `content`, `embedding`
  (`pgvector.django.VectorField`, 384 dimensions to match `bge-small`). Unique on
  `(document_version, chunk_index)`. Chunks are never edited in place — re-indexing a
  version deletes and recreates all of its chunks, so the chunk set is always consistent
  with the current `extracted_text`.
- `AssistantInteraction`: audit record of every question asked — `user` (`SET_NULL`, so
  a deleted account doesn't erase the interaction), `question`, `answer`, `citations`
  (JSON list of `{document_id, document_title, version_id, chunk_id}`). This is the same
  audit-first instinct as `apps.common.audit.AuditLog` and gives Module 12 (Analytics) a
  ready-made source later.

Infrastructure adapters, each isolated to one module so the LLM/embedding backend can
change without touching application logic:

- `infrastructure/embeddings.py`: `generate_embedding(text) -> list[float]`, POSTs to
  Ollama's `/api/embeddings` with `EMBEDDING_MODEL`.
- `infrastructure/llm.py`: `generate_answer(prompt) -> str`, POSTs to Ollama's
  `/api/generate` with `LLM_MODEL`, non-streaming.

Application services:

- `chunking_service.chunk_text`: fixed-size character chunking (1000 chars, 150 overlap)
  on whitespace boundaries. Not token-aware — see Future considerations.
- `indexing_service.reindex_document_version`: deletes existing chunks for a version,
  chunks `extracted_text`, embeds each chunk, and bulk-creates `DocumentChunk` rows.
  Idempotent by construction (delete-then-recreate), which is what makes re-indexing
  "repeatable" per the Phase 5 acceptance criterion.
- Triggered automatically: `apps.documents.application.tasks.extract_document_version_task`
  enqueues `apps.assistant.application.tasks.index_document_version_task` once extraction
  reaches `EXTRACTION_COMPLETED`. This is a direct cross-app call, following the existing
  precedent in this codebase of one module invoking another's application layer directly
  (e.g. `apps.membership` posting dues to `apps.finance`'s ledger, `apps.events` calling
  `apps.notifications.enqueue_notification`) rather than introducing a signal/event bus
  for a two-module dependency.
- `retrieval_service.search_relevant_chunks`: embeds the question, then orders
  `DocumentChunk` by `CosineDistance('embedding', query_embedding)`, restricted to chunks
  whose `DocumentVersion.document` is in
  `apps.documents.application.document_service.visible_documents_queryset(user)`. This is
  the permission-respecting step: a user never receives citations from a document their
  role/visibility tier doesn't allow, regardless of how relevant the chunk is.
- `assistant_service.answer_question`: if retrieval returns zero chunks, returns a fixed
  "I don't have authorized information to answer that" response **without calling the
  LLM** — this is what makes "never answer from memory alone" a hard guarantee rather
  than a prompt instruction the model could ignore. Otherwise builds a numbered-context
  prompt instructing the model to answer only from the provided context and to cite
  sources by number, calls the LLM, and returns `{answer, citations}` where citations map
  1:1 to the numbered context. Every call is persisted as an `AssistantInteraction`.

API: `POST /api/assistant/query/` (authenticated — any logged-in user; visibility
filtering already scopes down to what that user is allowed to see, so no separate
staff-only gate is needed here).

Re-indexing is also exposed as a management command
(`python manage.py reindex_documents`) that re-runs indexing for every version with
completed extraction — the operational lever for "repeatable and observable" re-indexing
without needing a dedicated API endpoint.

## Consequences

- The assistant can only ever cite documents the asking user could already see via the
  Documents module's own access control — permission enforcement lives in one place
  (`visible_documents_queryset`) and both modules use it.
- No LLM call happens without retrieved context, so there is no code path where the
  assistant "answers from memory."
- Re-indexing is safe to re-run at any time (e.g. after a chunking-strategy change)
  because it fully replaces a version's chunks rather than trying to diff them.
- Every question/answer is auditable via `AssistantInteraction`.

## Future considerations

- Chunking is character-based, not token-aware. Fine at the current document volume;
  revisit with a proper tokenizer if answer quality suffers from chunk boundaries
  splitting mid-sentence too aggressively.
- No ANN index (HNSW/IVFFlat) on `embedding` yet — a full sequential scan is fine at
  today's document volume. Add `pgvector.django.HnswIndex` once chunk counts make that
  matter.
- No conversation memory — each query is independent. Multi-turn context is a
  deliberately separate feature, not silently bundled in here.
- No streaming responses yet; the LLM call is synchronous and blocking within the
  request. Acceptable for `qwen2.5:3b`'s latency today; revisit if the model or usage
  pattern changes.
