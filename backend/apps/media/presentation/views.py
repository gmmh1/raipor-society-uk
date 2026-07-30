from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.documents.infrastructure.storage import StorageError
from apps.identity.permissions import HasAnyRole
from apps.media.application.image_service import ImageError, get_image_bytes, upload_image
from apps.media.presentation.serializers import ImageUploadSerializer


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data["file"]

        try:
            filename = upload_image(
                content_type=uploaded_file.content_type or "application/octet-stream",
                data=uploaded_file.read(),
            )
        except ImageError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        path = reverse("media-image-serve", kwargs={"filename": filename})
        return Response(
            {"url": request.build_absolute_uri(path)}, status=status.HTTP_201_CREATED
        )


class ImageServeView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, filename):
        try:
            data, content_type = get_image_bytes(filename=filename)
        except (ImageError, StorageError):
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(data, content_type=content_type)
        response["Cache-Control"] = "public, max-age=31536000, immutable"
        return response
