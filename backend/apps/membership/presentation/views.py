from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.permissions import HasAnyRole
from apps.membership.application.lifecycle_service import (
    MembershipLifecycleError,
    get_or_create_membership_for_user,
    transition_membership_status,
)
from apps.membership.models import Membership
from apps.membership.presentation.serializers import MembershipSerializer, MembershipTransitionSerializer


class MyMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = get_or_create_membership_for_user(request.user)
        return Response(MembershipSerializer(membership).data)


class MembershipTransitionView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def post(self, request):
        serializer = MembershipTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership_id = serializer.validated_data["membership_id"]
        to_status = serializer.validated_data["to_status"]
        reason = serializer.validated_data.get("reason", "")

        try:
            membership = Membership.objects.get(id=membership_id)
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Membership not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            updated = transition_membership_status(membership, to_status, request.user, reason)
        except MembershipLifecycleError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MembershipSerializer(updated).data)
