from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.permissions import HasAnyRole
from apps.timeline.application.entry_service import TimelineError, create_entry, delete_entry
from apps.timeline.models import TimelineEntry
from apps.timeline.presentation.serializers import (
    TimelineEntryCreateSerializer,
    TimelineEntrySerializer,
)


class TimelineEntryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = ("admin", "volunteer")
            return [IsAuthenticated(), HasAnyRole()]
        return [AllowAny()]

    def get(self, _request):
        entries = TimelineEntry.objects.filter(is_published=True).order_by("-entry_date")
        return Response(TimelineEntrySerializer(entries, many=True).data)

    def post(self, request):
        serializer = TimelineEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            entry = create_entry(author=request.user, **serializer.validated_data)
        except TimelineError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(TimelineEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class AdminTimelineEntryListView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def get(self, _request):
        entries = TimelineEntry.objects.order_by("-entry_date")
        return Response(TimelineEntrySerializer(entries, many=True).data)


class TimelineEntryDeleteView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def post(self, _request, entry_id):
        try:
            entry = TimelineEntry.objects.get(id=entry_id)
        except TimelineEntry.DoesNotExist:
            return Response({"detail": "Entry not found."}, status=status.HTTP_404_NOT_FOUND)

        delete_entry(entry=entry)
        return Response(status=status.HTTP_204_NO_CONTENT)
