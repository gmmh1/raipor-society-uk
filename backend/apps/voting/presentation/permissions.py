from rest_framework.permissions import BasePermission

from apps.membership.domain.status import STATUS_ACTIVE
from apps.membership.models import Membership


class CanVote(BasePermission):
    """Voting is a right of adult, admin-approved membership — not gated by which
    role(s) or committee position someone additionally holds. An admin, volunteer,
    treasurer, adviser, etc. is still just a member and votes the same as anyone
    else; a staff role never substitutes for actual membership. Eligibility is
    purely: authenticated, not flagged as a minor (under 18 — see ``User.is_minor``),
    and an ``active`` Membership on file (the admin-approval step — see
    ``MembershipTransitionView``). A pending/suspended/expired/cancelled membership,
    or an account with no Membership at all, can't vote."""

    message = "You must be an active, adult member to vote."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_minor:
            return False
        return Membership.objects.filter(user=user, status=STATUS_ACTIVE).exists()
