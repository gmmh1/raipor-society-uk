from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.application.document_service import (
    DocumentError,
    archive_document,
    create_document,
    create_version,
    get_download_url,
    get_visible_document,
    search_documents,
)
from apps.documents.domain.types import STAFF_ROLES
from apps.documents.models import DocumentVersion
from apps.documents.presentation.serializers import (
    DocumentCreateSerializer,
    DocumentDownloadSerializer,
    DocumentSerializer,
    DocumentVersionSerializer,
    DocumentVersionUploadSerializer,
)
from apps.identity.permissions import HasAnyRole


class DocumentListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = STAFF_ROLES
            return [IsAuthenticated(), HasAnyRole()]
        return [AllowAny()]

    def get(self, request):
        query = request.query_params.get("q", "")
        documents = search_documents(user=request.user, query=query)
        return Response(DocumentSerializer(documents, many=True).data)

    def post(self, request):
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            document = create_document(owner=request.user, **serializer.validated_data)
        except DocumentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class DocumentDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, document_id):
        document = get_visible_document(user=request.user, document_id=document_id)
        if document is None:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DocumentSerializer(document).data)


class DocumentVersionUploadView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = STAFF_ROLES
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, document_id):
        document = get_visible_document(user=request.user, document_id=document_id)
        if document is None:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentVersionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data["file"]

        try:
            version = create_version(
                document=document,
                uploaded_by=request.user,
                original_filename=uploaded_file.name,
                content_type=uploaded_file.content_type or "application/octet-stream",
                data=uploaded_file.read(),
            )
        except DocumentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DocumentVersionSerializer(version).data, status=status.HTTP_201_CREATED)


class DocumentVersionDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, document_id, version_id):
        document = get_visible_document(user=request.user, document_id=document_id)
        if document is None:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            version = document.versions.get(id=version_id)
        except DocumentVersion.DoesNotExist:
            return Response({"detail": "Version not found."}, status=status.HTTP_404_NOT_FOUND)

        url = get_download_url(version=version)
        return Response(DocumentDownloadSerializer({"url": url}).data)


class DocumentArchiveView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = STAFF_ROLES

    def post(self, request, document_id):
        document = get_visible_document(user=request.user, document_id=document_id)
        if document is None:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        archive_document(document=document, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
