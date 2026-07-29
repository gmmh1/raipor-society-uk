from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.permissions import HasAnyRole
from apps.voting.application.poll_service import (
    VotingError,
    cast_vote,
    create_poll,
    get_results,
    get_visible_poll,
    visible_polls_queryset,
)
from apps.voting.domain.types import STAFF_ROLES
from apps.voting.models import PollOption
from apps.voting.presentation.serializers import (
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
    permission_classes = [IsAuthenticated]

    def post(self, request, poll_id):
        poll = get_visible_poll(user=request.user, poll_id=poll_id)
        if poll is None:
            return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)

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
