import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.assistant.application.assistant_service import answer_question
from apps.assistant.application.chunking_service import chunk_text
from apps.assistant.application.indexing_service import reindex_document_version
from apps.assistant.application.retrieval_service import search_relevant_chunks
from apps.assistant.domain.types import EMBEDDING_DIMENSIONS, NO_CONTEXT_ANSWER
from apps.assistant.models import AssistantInteraction, DocumentChunk
from apps.documents.domain.types import EXTRACTION_COMPLETED
from apps.documents.models import Document, DocumentVersion
from apps.identity.models import User


def _unit_vector(active_index: int) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSIONS
    vector[active_index] = 1.0
    return vector


def _make_version(
    document: Document, uploader: User, *, extracted_text: str, version_number: int = 1
):
    return DocumentVersion.objects.create(
        document=document,
        version_number=version_number,
        file_key=f"documents/{document.id}/v{version_number}/file.txt",
        original_filename="file.txt",
        content_type="text/plain",
        size_bytes=len(extracted_text),
        checksum_sha256="abc123",
        uploaded_by=uploader,
        extraction_status=EXTRACTION_COMPLETED,
        extracted_text=extracted_text,
    )


def test_chunk_text_empty_returns_no_chunks():
    assert chunk_text("   ") == []


def test_chunk_text_short_text_single_chunk():
    assert chunk_text("hello world", chunk_size=1000, overlap=150) == ["hello world"]


def test_chunk_text_long_text_produces_overlapping_chunks():
    text = "a" * 2500
    chunks = chunk_text(text, chunk_size=1000, overlap=150)
    assert len(chunks) == 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


@pytest.mark.django_db
def test_reindex_document_version_creates_and_replaces_chunks(monkeypatch):
    monkeypatch.setattr(
        "apps.assistant.application.indexing_service.generate_embedding",
        lambda text: _unit_vector(0),
    )

    owner = User.objects.create_user(username="assistant-owner-1", password="pass123")
    document = Document.objects.create(
        title="Policy", category="policy", visibility="public", owner=owner
    )
    version = _make_version(document, owner, extracted_text="a" * 2500)

    count = reindex_document_version(version=version)
    assert count == 3
    assert DocumentChunk.objects.filter(document_version=version).count() == 3

    # Re-running replaces rather than duplicates.
    count_again = reindex_document_version(version=version)
    assert count_again == 3
    assert DocumentChunk.objects.filter(document_version=version).count() == 3


@pytest.mark.django_db
def test_reindex_skips_versions_without_completed_extraction():
    owner = User.objects.create_user(username="assistant-owner-2", password="pass123")
    document = Document.objects.create(
        title="Draft", category="policy", visibility="public", owner=owner
    )
    version = DocumentVersion.objects.create(
        document=document,
        version_number=1,
        file_key="documents/x/v1/file.txt",
        original_filename="file.txt",
        content_type="text/plain",
        size_bytes=5,
        checksum_sha256="abc123",
        uploaded_by=owner,
    )

    assert reindex_document_version(version=version) == 0
    assert DocumentChunk.objects.filter(document_version=version).count() == 0


@pytest.mark.django_db
def test_search_relevant_chunks_respects_visibility_and_ranking(monkeypatch):
    monkeypatch.setattr(
        "apps.assistant.application.retrieval_service.generate_embedding",
        lambda text: _unit_vector(0),
    )

    owner = User.objects.create_user(username="assistant-owner-3", password="pass123")
    visible_doc = Document.objects.create(
        title="Visible", category="policy", visibility="public", owner=owner
    )
    hidden_doc = Document.objects.create(
        title="Hidden", category="policy", visibility="staff", owner=owner
    )
    visible_version = _make_version(visible_doc, owner, extracted_text="visible content")
    hidden_version = _make_version(
        hidden_doc, owner, extracted_text="hidden content", version_number=1
    )

    close_chunk = DocumentChunk.objects.create(
        document_version=visible_version,
        chunk_index=0,
        content="close",
        embedding=_unit_vector(0),
    )
    far_chunk = DocumentChunk.objects.create(
        document_version=visible_version, chunk_index=1, content="far", embedding=_unit_vector(1)
    )
    DocumentChunk.objects.create(
        document_version=hidden_version, chunk_index=0, content="secret", embedding=_unit_vector(0)
    )

    member = User.objects.create_user(username="assistant-member-1", password="pass123")
    results = search_relevant_chunks(user=member, question="anything")

    result_ids = [chunk.id for chunk in results]
    assert far_chunk.id in result_ids  # visible document's chunks all returned
    assert all(chunk.document_version_id == visible_version.id for chunk in results)
    assert results[0].id == close_chunk.id  # closer embedding ranks first


@pytest.mark.django_db
def test_answer_question_without_matching_chunks_does_not_call_llm(monkeypatch):
    monkeypatch.setattr(
        "apps.assistant.application.retrieval_service.generate_embedding",
        lambda text: _unit_vector(0),
    )

    def fail_if_called(prompt):
        raise AssertionError("LLM must not be called when there is no retrieved context.")

    monkeypatch.setattr(
        "apps.assistant.application.assistant_service.generate_answer", fail_if_called
    )

    user = User.objects.create_user(username="assistant-user-1", password="pass123")
    result = answer_question(user=user, question="What is the safeguarding policy?")

    assert result["answer"] == NO_CONTEXT_ANSWER
    assert result["citations"] == []
    interaction = AssistantInteraction.objects.get(user=user)
    assert interaction.answer == NO_CONTEXT_ANSWER


@pytest.mark.django_db
def test_answer_question_with_context_returns_citations(monkeypatch):
    monkeypatch.setattr(
        "apps.assistant.application.retrieval_service.generate_embedding",
        lambda text: _unit_vector(0),
    )
    monkeypatch.setattr(
        "apps.assistant.application.assistant_service.generate_answer",
        lambda prompt: "The policy requires two references [1].",
    )

    owner = User.objects.create_user(username="assistant-owner-4", password="pass123")
    document = Document.objects.create(
        title="Safeguarding Policy", category="policy", visibility="public", owner=owner
    )
    version = _make_version(document, owner, extracted_text="two references are required")
    DocumentChunk.objects.create(
        document_version=version,
        chunk_index=0,
        content="two references are required",
        embedding=_unit_vector(0),
    )

    user = User.objects.create_user(username="assistant-user-2", password="pass123")
    result = answer_question(user=user, question="How many references are required?")

    assert result["answer"] == "The policy requires two references [1]."
    assert len(result["citations"]) == 1
    assert result["citations"][0]["document_title"] == "Safeguarding Policy"

    interaction = AssistantInteraction.objects.get(user=user)
    assert interaction.citations[0]["document_id"] == str(document.id)


@pytest.mark.django_db
def test_assistant_query_endpoint_requires_authentication(monkeypatch):
    monkeypatch.setattr(
        "apps.assistant.application.retrieval_service.generate_embedding",
        lambda text: _unit_vector(0),
    )

    response = APIClient().post(
        reverse("assistant-query"), data={"question": "hello"}, format="json"
    )
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_assistant_query_endpoint_returns_answer(monkeypatch):
    monkeypatch.setattr(
        "apps.assistant.application.retrieval_service.generate_embedding",
        lambda text: _unit_vector(0),
    )
    monkeypatch.setattr(
        "apps.assistant.application.assistant_service.generate_answer",
        lambda prompt: "Answer text [1].",
    )

    owner = User.objects.create_user(username="assistant-owner-5", password="pass123")
    document = Document.objects.create(
        title="FAQ", category="other", visibility="public", owner=owner
    )
    version = _make_version(document, owner, extracted_text="some content")
    DocumentChunk.objects.create(
        document_version=version, chunk_index=0, content="some content", embedding=_unit_vector(0)
    )

    user = User.objects.create_user(username="assistant-user-3", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        reverse("assistant-query"), data={"question": "What is this?"}, format="json"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Answer text [1]."
    assert body["citations"][0]["document_title"] == "FAQ"


@pytest.mark.django_db
def test_extraction_completion_triggers_indexing_task(monkeypatch):
    from apps.documents.application.tasks import extract_document_version_task

    owner = User.objects.create_user(username="assistant-owner-6", password="pass123")
    document = Document.objects.create(
        title="Minutes", category="minutes", visibility="member", owner=owner
    )
    version = DocumentVersion.objects.create(
        document=document,
        version_number=1,
        file_key="documents/x/v1/file.txt",
        original_filename="file.txt",
        content_type="text/plain",
        size_bytes=5,
        checksum_sha256="abc123",
        uploaded_by=owner,
    )

    monkeypatch.setattr(
        "apps.documents.application.tasks.storage.download_bytes",
        lambda *, key: b"some extracted text",
    )

    delayed = {}
    monkeypatch.setattr(
        "apps.assistant.application.tasks.index_document_version_task.delay",
        lambda version_id: delayed.setdefault("version_id", version_id),
    )

    extract_document_version_task(str(version.id))

    version.refresh_from_db()
    assert version.extraction_status == EXTRACTION_COMPLETED
    assert delayed["version_id"] == str(version.id)
