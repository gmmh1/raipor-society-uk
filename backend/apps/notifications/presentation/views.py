from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import User
from apps.identity.permissions import HasAnyRole
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.models import Notification, PushSubscription
from apps.notifications.presentation.serializers import (
    NotificationSerializer,
    PushSubscriptionSerializer,
    RegisterPushSubscriptionRequestSerializer,
    SendNotificationSerializer,
    UnregisterPushSubscriptionRequestSerializer,
)


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


class PushSubscriptionRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterPushSubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription, _ = PushSubscription.objects.update_or_create(
            endpoint=serializer.validated_data["endpoint"],
            defaults={
                "user": request.user,
                "p256dh_key": serializer.validated_data["p256dh_key"],
                "auth_key": serializer.validated_data["auth_key"],
                "is_active": True,
            },
        )
        return Response(
            PushSubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED
        )


class PushSubscriptionUnregisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UnregisterPushSubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PushSubscription.objects.filter(
            user=request.user, endpoint=serializer.validated_data["endpoint"]
        ).update(is_active=False)
        return Response(status=status.HTTP_204_NO_CONTENT)
