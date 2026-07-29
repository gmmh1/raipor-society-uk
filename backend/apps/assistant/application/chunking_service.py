from apps.assistant.domain.types import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS


def chunk_text(
    text: str, *, chunk_size: int = CHUNK_SIZE_CHARS, overlap: int = CHUNK_OVERLAP_CHARS
) -> list[str]:
    text = text.strip()
    if not text:
        return []

    step = chunk_size - overlap
    chunks = []
    position = 0
    while position < len(text):
        chunk = text[position : position + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        position += step
    return chunks
