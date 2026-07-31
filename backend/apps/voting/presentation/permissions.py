from rest_framework.permissions import BasePermission

from apps.identity.application.rbac_service import user_has_any_role
from apps.identity.domain.roles import ROLE_MEMBER
from apps.membership.domain.status import STATUS_ACTIVE
from apps.membership.models import Membership


class CanVote(BasePermission):
    """Voting is restricted to adult, admin-approved members: must hold the
    ``member`` role, must not be flagged as a minor (under 18 — see
    ``User.is_minor``), and must have an ``active`` Membership (the admin-approval
    step — see ``MembershipTransitionView``). A pending/suspended/expired/cancelled
    membership, or an account never approved past "pending", can't vote."""

    message = "You must be an active, adult member to vote."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user.is_authenticated:
            return False
        if not user_has_any_role(user, (ROLE_MEMBER,)):
            return False
        if user.is_minor:
            return False
        return Membership.objects.filter(user=user, status=STATUS_ACTIVE).exists()
