from django.urls import path

from apps.notifications.presentation.views import MyNotificationsView, SendNotificationView

urlpatterns = [
    path("me/", MyNotificationsView.as_view(), name="notifications-me"),
    path("send/", SendNotificationView.as_view(), name="notifications-send"),
]
