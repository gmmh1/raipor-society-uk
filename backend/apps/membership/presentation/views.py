from django.db.models import Q
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsPagination
from apps.identity.models import User
from apps.identity.permissions import HasAnyRole
from apps.media.application.image_service import ImageError, upload_image
from apps.media.presentation.serializers import ImageUploadSerializer
from apps.membership.application.committee_service import (
    CommitteeError,
    create_committee,
    current_committee,
    get_committee_roster,
    list_committees,
    remove_committee_member,
    set_committee_position,
)
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
from apps.membership.application.member_admin_service import (
    MemberAdminError,
    create_member,
    erase_member,
    set_member_active,
    update_member_contact,
)
from apps.membership.application.profile_service import (
    get_or_create_profile_for_user,
    set_avatar_url,
    update_own_profile,
)
from apps.membership.application.tier_service import TierError, assign_tier, record_dues_payment
from apps.membership.domain.status import STATUS_CHOICES
from apps.membership.models import (
    Committee,
    GuardianRelationship,
    MemberProfile,
    Membership,
    MembershipTier,
)
from apps.membership.presentation.serializers import (
    AdminCreateMemberRequestSerializer,
    AdminEraseMemberRequestSerializer,
    AdminSetActiveRequestSerializer,
    AdminUpdateContactRequestSerializer,
    CommitteeCreateRequestSerializer,
    CommitteeMemberSerializer,
    CommitteeSerializer,
    DuesRecordRequestSerializer,
    GuardianConsentRequestSerializer,
    GuardianLinkRequestSerializer,
    GuardianRelationshipSerializer,
    MembershipAdminSerializer,
    MembershipSerializer,
    MembershipTierSerializer,
    MembershipTransitionSerializer,
    MyProfileSerializer,
    ProfileUpdateRequestSerializer,
    PublicProfileSerializer,
    SetCommitteeMemberRequestSerializer,
    TierAssignmentRequestSerializer,
)

VALID_STATUSES = {choice[0] for choice in STATUS_CHOICES}


class MyMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = get_or_create_membership_for_user(request.user)
        return Response(MembershipSerializer(membership).data)


class MemberDirectoryView(APIView):
    """Minimal name+photo lookup for picking election candidates — narrower than
    MembershipAdminListView (admin/treasurer-only, exposes status/billing data);
    volunteers who can create polls but not manage membership need this too."""

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        queryset = User.objects.filter(is_active=True).select_related("profile")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
            )
        queryset = queryset.order_by("first_name", "username")[:50]

        results = [
            {
                "user_id": str(user.id),
                "name": (f"{user.first_name} {user.last_name}".strip() or user.username),
                "username": user.username,
                "avatar_url": getattr(getattr(user, "profile", None), "avatar_url", "") or "",
            }
            for user in queryset
        ]
        return Response(results)


class MembershipAdminListView(APIView):
    """Admin/treasurer search over all memberships, paginated and filterable.

    Closes ADR 0003's "admin list/search endpoints" follow-up.
    """

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def get(self, request):
        queryset = Membership.objects.select_related("user", "user__profile", "tier").order_by(
            "-created_at"
        )

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


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile_for_user(request.user)
        return Response(MyProfileSerializer(profile).data)

    def post(self, request):
        serializer = ProfileUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_profile_for_user(request.user)
        updated = update_own_profile(profile=profile, **serializer.validated_data)
        return Response(MyProfileSerializer(updated).data)


class MyProfilePhotoView(APIView):
    """Any signed-in member can upload their own profile photo — separate from
    ``ImageUploadView`` (media app), which stays admin/volunteer-only for content
    images (events, blog, shop). This is the only self-service image upload path."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data["file"]

        try:
            filename = upload_image(
                content_type=uploaded_file.content_type or "application/octet-stream",
                data=uploaded_file.read(),
            )
        except ImageError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        path = reverse("media-image-serve", kwargs={"filename": filename})
        avatar_url = request.build_absolute_uri(path)
        set_avatar_url(user=request.user, avatar_url=avatar_url)
        return Response({"url": avatar_url}, status=status.HTTP_201_CREATED)


class CommitteeListCreateView(APIView):
    """Committee terms — e.g. "2024–2026 Committee". Listing is admin/volunteer
    (management use); only admins can create a new term."""

    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = ("admin",)
            return [IsAuthenticated(), HasAnyRole()]
        self.required_roles = ("admin", "volunteer")
        return [IsAuthenticated(), HasAnyRole()]

    def get(self, request):
        committees = list_committees()
        current = current_committee()
        context = {"current_committee_id": getattr(current, "id", None)}
        return Response(CommitteeSerializer(committees, many=True, context=context).data)

    def post(self, request):
        serializer = CommitteeCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            committee = create_committee(creator=request.user, **serializer.validated_data)
        except CommitteeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CommitteeSerializer(committee).data, status=status.HTTP_201_CREATED)


class CommitteeMembersView(APIView):
    """A specific committee's roster — full roster (regardless of public_consent)
    for admin/volunteer management; assigning a position is admin-only."""

    def get_permissions(self):
        self.required_roles = ("admin",) if self.request.method == "POST" else ("admin", "volunteer")
        return [IsAuthenticated(), HasAnyRole()]

    def get(self, _request, committee_id):
        try:
            committee = Committee.objects.get(id=committee_id)
        except Committee.DoesNotExist:
            return Response({"detail": "Committee not found."}, status=status.HTTP_404_NOT_FOUND)

        roster = get_committee_roster(committee=committee)
        return Response(CommitteeMemberSerializer(roster, many=True).data)

    def post(self, request, committee_id):
        try:
            committee = Committee.objects.get(id=committee_id)
        except Committee.DoesNotExist:
            return Response({"detail": "Committee not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SetCommitteeMemberRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            target_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            membership = set_committee_position(
                committee=committee, user=target_user, position=serializer.validated_data["position"]
            )
        except CommitteeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CommitteeMemberSerializer(membership).data, status=status.HTTP_201_CREATED)


class CommitteeMemberRemoveView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, _request, committee_id, user_id):
        try:
            committee = Committee.objects.get(id=committee_id)
        except Committee.DoesNotExist:
            return Response({"detail": "Committee not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        remove_committee_member(committee=committee, user=target_user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicCommitteeRosterView(APIView):
    """A single committee's public roster by id — including past committees, so
    they stay browsable from the timeline entry that references them."""

    permission_classes = [AllowAny]

    def get(self, _request, committee_id):
        try:
            committee = Committee.objects.get(id=committee_id)
        except Committee.DoesNotExist:
            return Response({"detail": "Committee not found."}, status=status.HTTP_404_NOT_FOUND)

        roster = get_committee_roster(committee=committee, public_only=True)
        return Response(
            {
                "committee": CommitteeSerializer(committee).data,
                "members": CommitteeMemberSerializer(roster, many=True).data,
            }
        )


class AdminCreateMemberView(APIView):
    """Manual member entry for people who joined offline (paper form, in person).
    Mirrors self-registration's requirements — phone and photo are mandatory here
    too — but skips email verification since an admin is vouching for the member,
    and sends a password-reset link instead of the admin choosing a password."""

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = AdminCreateMemberRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_url = request.data.get("avatar_url", "").strip()
        if not avatar_url:
            return Response(
                {"avatar_url": ["A profile photo is required."]}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = create_member(**serializer.validated_data, avatar_url=avatar_url)
        except MemberAdminError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": str(user.id), "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class AdminUpdateMemberContactView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = AdminUpdateContactRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            target_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        updated = update_member_contact(
            user=target_user,
            phone_number=serializer.validated_data.get("phone_number"),
            avatar_url=serializer.validated_data.get("avatar_url"),
        )
        return Response(
            {
                "user_id": str(updated.id),
                "phone_number": updated.phone_number,
                "avatar_url": getattr(getattr(updated, "profile", None), "avatar_url", "") or "",
            }
        )


class AdminSetMemberActiveView(APIView):
    """Deactivate/reactivate a member's account (soft delete — preserves the
    Membership/MemberProfile audit trail rather than destroying records)."""

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = AdminSetActiveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            target_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        updated = set_member_active(
            user=target_user, is_active=serializer.validated_data["is_active"]
        )
        return Response({"user_id": str(updated.id), "is_active": updated.is_active})


class AdminEraseMemberView(APIView):
    """GDPR right-to-erasure: scrubs a member's personal data (never a raw row
    delete — see erase_member's docstring for why that's unsafe on this schema).
    Irreversible; logged to AuditLog."""

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = AdminEraseMemberRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            target_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            erase_member(user=target_user, actor=request.user)
        except MemberAdminError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicRosterView(APIView):
    """Current-committee + general member cards for the public About Us page —
    only profiles the member themselves opted into (``public_consent``). Past
    committees aren't shown here — they're reached via their timeline entry (see
    PublicCommitteeRosterView)."""

    permission_classes = [AllowAny]

    def get(self, _request):
        committee = current_committee()
        memberships_by_user_id = {}
        if committee is not None:
            memberships_by_user_id = {
                membership.user_id: membership
                for membership in get_committee_roster(committee=committee)
            }

        consented = MemberProfile.objects.filter(public_consent=True).select_related("user")
        context = {"memberships_by_user_id": memberships_by_user_id}

        committee_profiles = sorted(
            (profile for profile in consented if profile.user_id in memberships_by_user_id),
            key=lambda profile: memberships_by_user_id[profile.user_id].display_order,
        )
        member_profiles = [
            profile for profile in consented if profile.user_id not in memberships_by_user_id
        ]

        return Response(
            {
                "committee": PublicProfileSerializer(committee_profiles, many=True, context=context).data,
                "members": PublicProfileSerializer(member_profiles, many=True, context=context).data,
            }
        )
