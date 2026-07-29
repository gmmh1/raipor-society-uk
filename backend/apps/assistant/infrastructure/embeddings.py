"""Embedding adapter for Ollama. Only this module knows the embeddings HTTP contract."""

import requests
from django.conf import settings


class EmbeddingError(RuntimeError):
    pass


def generate_embedding(text: str) -> list[float]:
    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/embeddings",
            json={"model": settings.EMBEDDING_MODEL, "prompt": text},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise EmbeddingError(f"Failed to generate embedding: {exc}") from exc

    embedding = response.json().get("embedding")
    if not embedding:
        raise EmbeddingError("Ollama returned no embedding.")
    return embedding
