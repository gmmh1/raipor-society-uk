from django.urls import path

from apps.notifications.presentation.views import (
    MyNotificationsView,
    PushSubscriptionRegisterView,
    PushSubscriptionUnregisterView,
    SendNotificationView,
)

urlpatterns = [
    path("me/", MyNotificationsView.as_view(), name="notifications-me"),
    path("send/", SendNotificationView.as_view(), name="notifications-send"),
    path(
        "push-subscriptions/",
        PushSubscriptionRegisterView.as_view(),
        name="notifications-push-subscribe",
    ),
    path(
        "push-subscriptions/unregister/",
        PushSubscriptionUnregisterView.as_view(),
        name="notifications-push-unsubscribe",
    ),
]
