from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.application.event_service import EventServiceError, check_in_registration, register_for_event
from apps.events.models import Event, EventRegistration
from apps.events.presentation.serializers import (
    EventCheckInRequestSerializer,
    EventRegistrationRequestSerializer,
    EventRegistrationSerializer,
    EventSerializer,
)
from apps.identity.permissions import HasAnyRole


class EventListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = ("admin", "volunteer")
            return [IsAuthenticated(), HasAnyRole()]
        return [AllowAny()]

    def get(self, _request):
        events = Event.objects.filter(is_published=True).order_by("starts_at")
        return Response(EventSerializer(events, many=True).data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(created_by=request.user)
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)


class EventRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventRegistrationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_id = serializer.validated_data["event_id"]
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            registration = register_for_event(event, request.user)
        except EventServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(EventRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)


class EventCheckInView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def post(self, request):
        serializer = EventCheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registration_id = serializer.validated_data["registration_id"]
        try:
            registration = EventRegistration.objects.get(id=registration_id)
        except EventRegistration.DoesNotExist:
            return Response({"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            checked_in = check_in_registration(registration, request.user)
        except EventServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(EventRegistrationSerializer(checked_in).data)
