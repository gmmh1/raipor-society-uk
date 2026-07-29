"""LLM generation adapter for Ollama. Only this module knows the generate HTTP contract."""

import requests
from django.conf import settings


class LLMError(RuntimeError):
    pass


def generate_answer(prompt: str) -> str:
    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={"model": settings.LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMError(f"Failed to generate answer: {exc}") from exc

    answer = response.json().get("response", "").strip()
    if not answer:
        raise LLMError("Ollama returned an empty response.")
    return answer
