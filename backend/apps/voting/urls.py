from django.urls import path

from apps.voting.presentation.views import (
    CastVoteView,
    PollDetailView,
    PollListCreateView,
    PollResultsView,
)

urlpatterns = [
    path("polls/", PollListCreateView.as_view(), name="voting-polls-list-create"),
    path("polls/<uuid:poll_id>/", PollDetailView.as_view(), name="voting-polls-detail"),
    path("polls/<uuid:poll_id>/vote/", CastVoteView.as_view(), name="voting-polls-vote"),
    path("polls/<uuid:poll_id>/results/", PollResultsView.as_view(), name="voting-polls-results"),
]
