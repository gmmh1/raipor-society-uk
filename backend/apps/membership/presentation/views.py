from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsPagination
from apps.identity.models import User
from apps.identity.permissions import HasAnyRole
from apps.membership.application.guardian_service import (
    GuardianRelationshipError,
    link_guardian,
    record_guardian_consent,
)
from apps.membership.application.lifecycle_service import (
    MembershipLifecycleError,
    get_or_create_membership_for_user,
    transition_membership_status,
)
from apps.membership.application.tier_service import TierError, assign_tier, record_dues_payment
from apps.membership.domain.status import STATUS_CHOICES
from apps.membership.models import GuardianRelationship, Membership, MembershipTier
from apps.membership.presentation.serializers import (
    DuesRecordRequestSerializer,
    GuardianConsentRequestSerializer,
    GuardianLinkRequestSerializer,
    GuardianRelationshipSerializer,
    MembershipAdminSerializer,
    MembershipSerializer,
    MembershipTierSerializer,
    MembershipTransitionSerializer,
    TierAssignmentRequestSerializer,
)

VALID_STATUSES = {choice[0] for choice in STATUS_CHOICES}


class MyMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = get_or_create_membership_for_user(request.user)
        return Response(MembershipSerializer(membership).data)


class MembershipAdminListView(APIView):
    """Admin/treasurer search over all memberships, paginated and filterable.

    Closes ADR 0003's "admin list/search endpoints" follow-up.
    """

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def get(self, request):
        queryset = Membership.objects.select_related("user", "tier").order_by("-created_at")

        status_filter = request.query_params.get("status", "").strip()
        if status_filter:
            if status_filter not in VALID_STATUSES:
                return Response(
                    {"detail": f"Unknown status '{status_filter}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(status=status_filter)

        tier_filter = request.query_params.get("tier", "").strip()
        if tier_filter:
            queryset = queryset.filter(tier__code=tier_filter)

        query = request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query)
                | Q(user__email__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
            )

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = MembershipAdminSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


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


class GuardianLinkView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = GuardianLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            guardian = User.objects.get(id=serializer.validated_data["guardian_id"])
            child = User.objects.get(id=serializer.validated_data["child_id"])
        except User.DoesNotExist:
            return Response(
                {"detail": "Guardian or child user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            relationship = link_guardian(
                guardian=guardian,
                child=child,
                relationship_type=serializer.validated_data["relationship_type"],
                actor=request.user,
            )
        except GuardianRelationshipError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            GuardianRelationshipSerializer(relationship).data, status=status.HTTP_201_CREATED
        )


class GuardianConsentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GuardianConsentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            relationship_id = serializer.validated_data["relationship_id"]
            relationship = GuardianRelationship.objects.get(id=relationship_id)
        except GuardianRelationship.DoesNotExist:
            return Response(
                {"detail": "Relationship not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            updated = record_guardian_consent(relationship=relationship, actor=request.user)
        except GuardianRelationshipError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(GuardianRelationshipSerializer(updated).data)


class MyGuardianRelationshipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        relationships = GuardianRelationship.objects.filter(
            Q(guardian=request.user) | Q(child=request.user)
        )
        return Response(GuardianRelationshipSerializer(relationships, many=True).data)


class MembershipTierListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = ("admin",)
            return [IsAuthenticated(), HasAnyRole()]
        return [IsAuthenticated()]

    def get(self, _request):
        tiers = MembershipTier.objects.filter(is_active=True).order_by("name")
        return Response(MembershipTierSerializer(tiers, many=True).data)

    def post(self, request):
        serializer = MembershipTierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tier = serializer.save()
        return Response(MembershipTierSerializer(tier).data, status=status.HTTP_201_CREATED)


class TierAssignmentView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def post(self, request):
        serializer = TierAssignmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = Membership.objects.get(id=serializer.validated_data["membership_id"])
            tier = MembershipTier.objects.get(code=serializer.validated_data["tier_code"])
        except (Membership.DoesNotExist, MembershipTier.DoesNotExist):
            return Response(
                {"detail": "Membership or tier not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            updated = assign_tier(membership=membership, tier=tier)
        except TierError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MembershipSerializer(updated).data)


class DuesRecordView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def post(self, request):
        serializer = DuesRecordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = Membership.objects.get(id=serializer.validated_data["membership_id"])
        except Membership.DoesNotExist:
            return Response({"detail": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            updated = record_dues_payment(
                membership=membership,
                actor=request.user,
                reference=serializer.validated_data.get("reference", ""),
            )
        except TierError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MembershipSerializer(updated).data)
