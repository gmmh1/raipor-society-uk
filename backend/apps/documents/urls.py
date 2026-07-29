from django.urls import path

from apps.documents.presentation.views import (
    DocumentArchiveView,
    DocumentDetailView,
    DocumentListCreateView,
    DocumentVersionDownloadView,
    DocumentVersionUploadView,
)

urlpatterns = [
    path("", DocumentListCreateView.as_view(), name="documents-list-create"),
    path("<uuid:document_id>/", DocumentDetailView.as_view(), name="documents-detail"),
    path(
        "<uuid:document_id>/versions/",
        DocumentVersionUploadView.as_view(),
        name="documents-version-upload",
    ),
    path(
        "<uuid:document_id>/versions/<uuid:version_id>/download/",
        DocumentVersionDownloadView.as_view(),
        name="documents-version-download",
    ),
    path("<uuid:document_id>/archive/", DocumentArchiveView.as_view(), name="documents-archive"),
]
