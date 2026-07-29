from django.contrib import admin

from apps.assistant.models import AssistantInteraction, DocumentChunk


@admin.register(AssistantInteraction)
class AssistantInteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "created_at")
    search_fields = ("question", "answer", "user__username")
    readonly_fields = ("user", "question", "answer", "citations", "created_at", "updated_at")


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "document_version", "chunk_index", "created_at")
    search_fields = ("content",)
    readonly_fields = ("document_version", "chunk_index", "content", "embedding")
