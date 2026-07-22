from celery import shared_task
from django.utils import timezone

from apps.membership.domain.status import STATUS_ACTIVE, STATUS_EXPIRED


@shared_task
def expire_memberships_task() -> int:
    from apps.membership.application.lifecycle_service import transition_membership_status
    from apps.membership.models import Membership

    now = timezone.now()
    due = Membership.objects.filter(
        status=STATUS_ACTIVE, expires_at__isnull=False, expires_at__lte=now
    )

    count = 0
    for membership in due:
        transition_membership_status(
            membership,
            STATUS_EXPIRED,
            actor=None,
            reason="Automatic expiry: membership period ended.",
        )
        count += 1
    return count
