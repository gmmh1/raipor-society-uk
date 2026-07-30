from django.urls import path

from apps.timeline.presentation.views import (
    AdminTimelineEntryListView,
    TimelineEntryDeleteView,
    TimelineEntryListCreateView,
)

urlpatterns = [
    path("entries/", TimelineEntryListCreateView.as_view(), name="timeline-entries-list-create"),
    path("entries/admin/", AdminTimelineEntryListView.as_view(), name="timeline-entries-admin-list"),
    path("entries/<uuid:entry_id>/delete/", TimelineEntryDeleteView.as_view(), name="timeline-entries-delete"),
]
