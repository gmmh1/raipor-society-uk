from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.permissions import HasAnyRole
from apps.voting.application.poll_service import (
    VotingError,
    cast_ranked_vote,
    cast_vote,
    create_poll,
    get_results,
    get_visible_poll,
    visible_polls_queryset,
)
from apps.voting.domain.types import STAFF_ROLES, VOTING_METHOD_RANKED_CHOICE
from apps.voting.models import PollOption
from apps.voting.presentation.permissions import CanVote
from apps.voting.presentation.serializers import (
    CastRankedVoteRequestSerializer,
    CastVoteRequestSerializer,
    PollCreateSerializer,
    PollSerializer,
)


class PollListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = STAFF_ROLES
            return [IsAuthenticated(), HasAnyRole()]
        return [AllowAny()]

    def get(self, request):
        polls = visible_polls_queryset(request.user).order_by("-opens_at")
        serializer = PollSerializer(polls, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = PollCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            poll = create_poll(creator=request.user, **serializer.validated_data)
        except VotingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = PollSerializer(poll, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PollDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, poll_id):
        poll = get_visible_poll(user=request.user, poll_id=poll_id)
        if poll is None:
            return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PollSerializer(poll, context={"request": request})
        return Response(serializer.data)


class CastVoteView(APIView):
    """Voting is restricted to adult, admin-approved members — see ``CanVote``."""

    permission_classes = [CanVote]

    def post(self, request, poll_id):
        poll = get_visible_poll(user=request.user, poll_id=poll_id)
        if poll is None:
            return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)

        if poll.voting_method == VOTING_METHOD_RANKED_CHOICE:
            return self._cast_ranked(request, poll)
        return self._cast_plurality(request, poll)

    def _cast_plurality(self, request, poll):
        serializer = CastVoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            option = PollOption.objects.get(id=serializer.validated_data["option_id"])
        except PollOption.DoesNotExist:
            return Response({"detail": "Option not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cast_vote(poll=poll, option=option, user=request.user)
        except VotingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    def _cast_ranked(self, request, poll):
        serializer = CastRankedVoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        option_ids = serializer.validated_data["ranked_option_ids"]
        options_by_id = {
            option.id: option for option in PollOption.objects.filter(id__in=option_ids)
        }
        if len(options_by_id) != len(set(option_ids)):
            return Response({"detail": "One or more options not found."}, status=status.HTTP_404_NOT_FOUND)
        ranked_options = [options_by_id[option_id] for option_id in option_ids]

        try:
            cast_ranked_vote(poll=poll, ranked_options=ranked_options, user=request.user)
        except VotingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class PollResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, poll_id):
        poll = get_visible_poll(user=request.user, poll_id=poll_id)
        if poll is None:
            return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            results = get_results(poll=poll, user=request.user)
        except VotingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(results)
