from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import User
from apps.identity.permissions import HasAnyRole
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.models import Notification
from apps.notifications.presentation.serializers import NotificationSerializer, SendNotificationSerializer


class MyNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")
        return Response(NotificationSerializer(notifications, many=True).data)


class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            recipient = User.objects.get(id=serializer.validated_data["recipient_id"])
        except User.DoesNotExist:
            return Response({"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)

        notification = enqueue_notification(
            recipient=recipient,
            channel=serializer.validated_data["channel"],
            subject=serializer.validated_data.get("subject", ""),
            body=serializer.validated_data["body"],
            context=serializer.validated_data.get("context", {}),
        )
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
