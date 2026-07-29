import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from apps.documents.infrastructure import extraction
from apps.documents.models import Document, DocumentVersion
from apps.identity.models import Role, User


def _make_staff_user(username: str) -> User:
    user = User.objects.create_user(username=username, password="pass123")
    role, _ = Role.objects.get_or_create(code="volunteer", defaults={"name": "Volunteer"})
    user.roles.add(role)
    return user


@pytest.mark.django_db
def test_visibility_filters_document_list():
    owner = User.objects.create_user(username="doc-owner-1", password="pass123")
    public_doc = Document.objects.create(
        title="Public Doc", category="policy", visibility="public", owner=owner
    )
    member_doc = Document.objects.create(
        title="Member Doc", category="policy", visibility="member", owner=owner
    )
    staff_doc = Document.objects.create(
        title="Staff Doc", category="policy", visibility="staff", owner=owner
    )

    anon_response = APIClient().get(reverse("documents-list-create"))
    anon_titles = {item["title"] for item in anon_response.json()}
    assert anon_titles == {public_doc.title}

    member = User.objects.create_user(username="doc-member-1", password="pass123")
    member_client = APIClient()
    member_client.force_authenticate(user=member)
    member_response = member_client.get(reverse("documents-list-create"))
    member_titles = {item["title"] for item in member_response.json()}
    assert member_titles == {public_doc.title, member_doc.title}

    staff = _make_staff_user("doc-staff-1")
    staff_client = APIClient()
    staff_client.force_authenticate(user=staff)
    staff_response = staff_client.get(reverse("documents-list-create"))
    staff_titles = {item["title"] for item in staff_response.json()}
    assert staff_titles == {public_doc.title, member_doc.title, staff_doc.title}


@pytest.mark.django_db
def test_document_create_requires_staff_role():
    member = User.objects.create_user(username="doc-member-2", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    forbidden = client.post(
        reverse("documents-list-create"),
        data={"title": "New Doc", "category": "policy", "visibility": "member"},
        format="json",
    )
    assert forbidden.status_code == 403

    staff = _make_staff_user("doc-staff-2")
    client.force_authenticate(user=staff)
    allowed = client.post(
        reverse("documents-list-create"),
        data={"title": "New Doc", "category": "policy", "visibility": "member"},
        format="json",
    )
    assert allowed.status_code == 201
    assert Document.objects.filter(title="New Doc").exists()


@pytest.mark.django_db
def test_version_upload_requires_staff_and_queues_extraction(monkeypatch):
    uploaded = {}

    def fake_upload_bytes(*, key, data, content_type):
        uploaded["key"] = key
        uploaded["data"] = data
        uploaded["content_type"] = content_type

    monkeypatch.setattr(
        "apps.documents.application.document_service.storage.upload_bytes", fake_upload_bytes
    )

    delayed = {}

    def fake_delay(version_id):
        delayed["version_id"] = version_id

    monkeypatch.setattr(
        "apps.documents.application.tasks.extract_document_version_task.delay", fake_delay
    )

    staff = _make_staff_user("doc-staff-3")
    owner = User.objects.create_user(username="doc-owner-2", password="pass123")
    document = Document.objects.create(
        title="Minutes", category="minutes", visibility="member", owner=owner
    )

    client = APIClient()
    client.force_authenticate(user=staff)

    upload_file = SimpleUploadedFile(
        "minutes.txt", b"Meeting minutes content", content_type="text/plain"
    )
    response = client.post(
        reverse("documents-version-upload", kwargs={"document_id": document.id}),
        data={"file": upload_file},
        format="multipart",
    )

    assert response.status_code == 201
    assert response.json()["version_number"] == 1
    assert uploaded["content_type"] == "text/plain"
    assert uploaded["data"] == b"Meeting minutes content"

    version = DocumentVersion.objects.get(document=document, version_number=1)
    assert version.checksum_sha256

    non_staff = User.objects.create_user(username="doc-member-3", password="pass123")
    client.force_authenticate(user=non_staff)
    forbidden = client.post(
        reverse("documents-version-upload", kwargs={"document_id": document.id}),
        data={"file": SimpleUploadedFile("x.txt", b"x", content_type="text/plain")},
        format="multipart",
    )
    assert forbidden.status_code == 403


@pytest.mark.django_db
def test_download_returns_presigned_url(monkeypatch):
    monkeypatch.setattr(
        "apps.documents.application.document_service.storage.generate_presigned_download_url",
        lambda *, key, expires_in=3600: f"https://minio.example/{key}",
    )

    owner = User.objects.create_user(username="doc-owner-3", password="pass123")
    document = Document.objects.create(
        title="Policy", category="policy", visibility="public", owner=owner
    )
    version = DocumentVersion.objects.create(
        document=document,
        version_number=1,
        file_key="documents/abc/v1/policy.pdf",
        original_filename="policy.pdf",
        content_type="application/pdf",
        size_bytes=10,
        checksum_sha256="deadbeef",
        uploaded_by=owner,
    )

    response = APIClient().get(
        reverse(
            "documents-version-download",
            kwargs={"document_id": document.id, "version_id": version.id},
        )
    )
    assert response.status_code == 200
    assert response.json()["url"] == "https://minio.example/documents/abc/v1/policy.pdf"


@pytest.mark.django_db
def test_archive_document_soft_deletes_and_hides_from_list():
    staff = _make_staff_user("doc-staff-4")
    document = Document.objects.create(
        title="Old Policy", category="policy", visibility="public", owner=staff
    )

    client = APIClient()
    client.force_authenticate(user=staff)
    response = client.post(reverse("documents-archive", kwargs={"document_id": document.id}))
    assert response.status_code == 204

    assert Document.objects.filter(id=document.id).count() == 0
    archived = Document.all_objects.get(id=document.id)
    assert archived.deleted_at is not None

    listing = APIClient().get(reverse("documents-list-create"))
    assert all(item["title"] != "Old Policy" for item in listing.json())


@pytest.mark.django_db
def test_search_matches_title_and_extracted_text():
    owner = User.objects.create_user(username="doc-owner-4", password="pass123")
    matching = Document.objects.create(
        title="Safeguarding Policy", category="policy", visibility="public", owner=owner
    )
    other = Document.objects.create(
        title="Unrelated", category="policy", visibility="public", owner=owner
    )
    DocumentVersion.objects.create(
        document=other,
        version_number=1,
        file_key="documents/other/v1/file.txt",
        original_filename="file.txt",
        content_type="text/plain",
        size_bytes=5,
        checksum_sha256="abc123",
        uploaded_by=owner,
        extracted_text="mentions safeguarding procedures in appendix",
    )

    response = APIClient().get(reverse("documents-list-create"), {"q": "safeguarding"})
    titles = {item["title"] for item in response.json()}
    assert titles == {matching.title, other.title}

    no_match = APIClient().get(reverse("documents-list-create"), {"q": "nonexistent-term"})
    assert no_match.json() == []


def test_extract_text_plain_decodes_utf8():
    assert extraction.extract_text(content_type="text/plain", data=b"hello world") == "hello world"


def test_extract_text_unsupported_content_type_raises():
    with pytest.raises(extraction.UnsupportedContentTypeError):
        extraction.extract_text(content_type="application/zip", data=b"binary")
