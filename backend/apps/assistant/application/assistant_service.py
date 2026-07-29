from apps.assistant.application.retrieval_service import search_relevant_chunks
from apps.assistant.domain.types import NO_CONTEXT_ANSWER
from apps.assistant.infrastructure.llm import generate_answer
from apps.assistant.models import AssistantInteraction

PROMPT_INSTRUCTIONS = (
    "Answer the question using only the numbered context below. "
    "Cite sources inline using their number in square brackets, e.g. [1]. "
    "If the context does not contain the answer, say you don't know."
)


def answer_question(*, user, question: str) -> dict:
    chunks = search_relevant_chunks(user=user, question=question)
    actor = user if getattr(user, "is_authenticated", False) else None

    if not chunks:
        interaction = AssistantInteraction.objects.create(
            user=actor, question=question, answer=NO_CONTEXT_ANSWER, citations=[]
        )
        return {"answer": interaction.answer, "citations": []}

    context_blocks = []
    citations = []
    for index, chunk in enumerate(chunks, start=1):
        document = chunk.document_version.document
        context_blocks.append(f"[{index}] {chunk.content}")
        citations.append(
            {
                "document_id": str(document.id),
                "document_title": document.title,
                "version_id": str(chunk.document_version.id),
                "chunk_id": str(chunk.id),
            }
        )

    prompt = (
        f"{PROMPT_INSTRUCTIONS}\n\n"
        + "\n\n".join(context_blocks)
        + f"\n\nQuestion: {question}\nAnswer:"
    )
    answer = generate_answer(prompt)

    interaction = AssistantInteraction.objects.create(
        user=actor, question=question, answer=answer, citations=citations
    )
    return {"answer": interaction.answer, "citations": citations}
