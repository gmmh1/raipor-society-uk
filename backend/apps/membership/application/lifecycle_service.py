from django.db import transaction
from django.utils import timezone

from apps.membership.application.guardian_service import has_active_consent
from apps.membership.domain.status import ALLOWED_TRANSITIONS, STATUS_ACTIVE, STATUS_EXPIRED
from apps.membership.models import Membership, MembershipStatusTransition
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.domain.types import CHANNEL_EMAIL


class MembershipLifecycleError(ValueError):
    pass


@transaction.atomic
def get_or_create_membership_for_user(user) -> Membership:
    membership, _ = Membership.objects.get_or_create(user=user)
    return membership


@transaction.atomic
def transition_membership_status(
    membership: Membership,
    new_status: str,
    actor,
    reason: str = "",
) -> Membership:
    current_status = membership.status
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())

    if new_status == current_status:
        raise MembershipLifecycleError("Membership is already in the requested status.")

    if new_status not in allowed:
        raise MembershipLifecycleError(
            f"Invalid transition from '{current_status}' to '{new_status}'."
        )

    activating_unconsented_minor = (
        new_status == STATUS_ACTIVE
        and membership.user.is_minor
        and not has_active_consent(child=membership.user)
    )
    if activating_unconsented_minor:
        raise MembershipLifecycleError(
            "A minor's membership cannot be activated without recorded guardian consent."
        )

    membership.status = new_status
    if new_status == STATUS_ACTIVE and membership.started_at is None:
        membership.started_at = timezone.now()
    if new_status == STATUS_EXPIRED:
        membership.ended_at = timezone.now()
    membership.save(update_fields=["status", "started_at", "ended_at", "updated_at"])

    MembershipStatusTransition.objects.create(
        membership=membership,
        from_status=current_status,
        to_status=new_status,
        reason=reason,
        changed_by=actor,
    )

    enqueue_notification(
        recipient=membership.user,
        channel=CHANNEL_EMAIL,
        subject="Membership status updated",
        body=f"Your membership status changed from {current_status} to {new_status}.",
        context={
            "membership_id": str(membership.id),
            "from_status": current_status,
            "to_status": new_status,
        },
    )
    return membership
