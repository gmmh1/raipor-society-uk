import uuid

from apps.documents.infrastructure import storage

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB — cover/product photos, not archival originals.

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


class ImageError(ValueError):
    pass


def upload_image(*, content_type: str, data: bytes) -> str:
    """Uploads an admin-supplied cover/product image to object storage and returns
    the storage filename (not a full URL — the caller builds the public-facing URL,
    since only it knows the deployment's externally-visible host)."""
    extension = ALLOWED_CONTENT_TYPES.get(content_type)
    if extension is None:
        raise ImageError(
            f"Unsupported image type '{content_type}'. Allowed: "
            f"{', '.join(sorted(ALLOWED_CONTENT_TYPES))}."
        )
    if not data:
        raise ImageError("Uploaded file is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise ImageError(f"Image exceeds the {MAX_IMAGE_BYTES // (1024 * 1024)}MB limit.")

    filename = f"{uuid.uuid4().hex}.{extension}"
    storage.upload_bytes(key=f"images/{filename}", data=data, content_type=content_type)
    return filename


# Reverse map for serving: filename extension -> content type.
CONTENT_TYPE_BY_EXTENSION = {ext: content_type for content_type, ext in ALLOWED_CONTENT_TYPES.items()}


def get_image_bytes(*, filename: str) -> tuple[bytes, str]:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    content_type = CONTENT_TYPE_BY_EXTENSION.get(extension)
    if content_type is None:
        raise ImageError("Unknown image type.")

    data = storage.download_bytes(key=f"images/{filename}")
    return data, content_type
