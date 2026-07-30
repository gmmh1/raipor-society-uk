import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User


@pytest.mark.django_db
def test_image_upload_requires_admin_or_volunteer_role():
    user = User.objects.create_user(username="media-user-1", password="pass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("media-image-upload"),
        data={"file": SimpleUploadedFile("photo.jpg", b"fake-bytes", content_type="image/jpeg")},
        format="multipart",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_image_upload_rejects_non_image_content_type():
    admin = User.objects.create_user(username="media-admin-1", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        reverse("media-image-upload"),
        data={"file": SimpleUploadedFile("virus.exe", b"not-an-image", content_type="application/x-msdownload")},
        format="multipart",
    )

    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


@pytest.mark.django_db
def test_image_upload_rejects_oversized_file():
    admin = User.objects.create_user(username="media-admin-2", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)

    oversized = SimpleUploadedFile(
        "big.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg"
    )
    response = client.post(
        reverse("media-image-upload"), data={"file": oversized}, format="multipart"
    )

    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()


@pytest.mark.django_db
def test_image_upload_and_serve_round_trip(monkeypatch):
    store: dict[str, bytes] = {}

    def fake_upload_bytes(*, key, data, content_type):
        store[key] = data

    def fake_download_bytes(*, key):
        return store[key]

    monkeypatch.setattr("apps.media.application.image_service.storage.upload_bytes", fake_upload_bytes)
    monkeypatch.setattr(
        "apps.media.application.image_service.storage.download_bytes", fake_download_bytes
    )

    admin = User.objects.create_user(username="media-admin-3", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)

    upload_response = client.post(
        reverse("media-image-upload"),
        data={"file": SimpleUploadedFile("photo.png", b"png-bytes", content_type="image/png")},
        format="multipart",
    )

    assert upload_response.status_code == 201
    url = upload_response.json()["url"]
    assert url.endswith(".png/")

    filename = url.rstrip("/").rsplit("/", 1)[-1]
    serve_response = APIClient().get(reverse("media-image-serve", kwargs={"filename": filename}))

    assert serve_response.status_code == 200
    assert serve_response.content == b"png-bytes"
    assert serve_response["Content-Type"] == "image/png"


@pytest.mark.django_db
def test_serve_unknown_image_returns_404():
    client = APIClient()
    response = client.get(reverse("media-image-serve", kwargs={"filename": "nope.png"}))
    assert response.status_code == 404
