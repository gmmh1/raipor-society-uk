"""Text extraction adapters, dispatched by content type.

Only this module imports the extraction libraries (pypdf, pytesseract, Pillow) so a
future format or engine change stays contained here.
"""

import io

import pypdf
import pytesseract
from PIL import Image

TEXT_CONTENT_TYPES = {"text/plain", "text/markdown"}
PDF_CONTENT_TYPES = {"application/pdf"}
IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/tiff"}

SUPPORTED_CONTENT_TYPES = TEXT_CONTENT_TYPES | PDF_CONTENT_TYPES | IMAGE_CONTENT_TYPES


class ExtractionError(RuntimeError):
    pass


class UnsupportedContentTypeError(ExtractionError):
    pass


def extract_text(*, content_type: str, data: bytes) -> str:
    if content_type in TEXT_CONTENT_TYPES:
        return _extract_plain_text(data)
    if content_type in PDF_CONTENT_TYPES:
        return _extract_pdf_text(data)
    if content_type in IMAGE_CONTENT_TYPES:
        return _extract_image_text(data)
    raise UnsupportedContentTypeError(f"No extractor registered for content type '{content_type}'.")


def _extract_plain_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _extract_pdf_text(data: bytes) -> str:
    try:
        reader = pypdf.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ExtractionError(f"Failed to extract PDF text: {exc}") from exc
    return "\n\n".join(pages).strip()


def _extract_image_text(data: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(image).strip()
    except Exception as exc:
        raise ExtractionError(f"Failed to OCR image: {exc}") from exc
