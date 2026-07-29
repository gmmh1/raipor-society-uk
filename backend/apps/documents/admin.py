from django.contrib import admin

from apps.documents.models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = (
        "version_number",
        "original_filename",
        "content_type",
        "size_bytes",
        "checksum_sha256",
        "extraction_status",
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "visibility", "owner", "created_at")
    list_filter = ("category", "visibility")
    search_fields = ("title", "description")
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "version_number", "extraction_status", "created_at")
    list_filter = ("extraction_status",)
    search_fields = ("original_filename", "document__title")
