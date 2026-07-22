from django.urls import path

from apps.events.presentation.views import (
    EventCancelRegistrationView,
    EventCancelView,
    EventCheckInView,
    EventListCreateView,
    EventRegisterView,
)

urlpatterns = [
    path("", EventListCreateView.as_view(), name="events-list-create"),
    path("register/", EventRegisterView.as_view(), name="events-register"),
    path("attendance/check-in/", EventCheckInView.as_view(), name="events-check-in"),
    path("<uuid:event_id>/cancel/", EventCancelView.as_view(), name="events-cancel"),
    path(
        "registrations/<uuid:registration_id>/cancel/",
        EventCancelRegistrationView.as_view(),
        name="events-registration-cancel",
    ),
]
