from django.urls import path

from apps.events.presentation.views import EventCheckInView, EventListCreateView, EventRegisterView

urlpatterns = [
    path("", EventListCreateView.as_view(), name="events-list-create"),
    path("register/", EventRegisterView.as_view(), name="events-register"),
    path("attendance/check-in/", EventCheckInView.as_view(), name="events-check-in"),
]
