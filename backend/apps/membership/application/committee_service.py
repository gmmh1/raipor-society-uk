from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.membership.domain.position import POSITION_DISPLAY_ORDER
from apps.membership.models import Committee, CommitteeMembership


class CommitteeError(ValueError):
    pass


def list_committees():
    return Committee.objects.all().order_by("-starts_at")


def current_committee() -> Committee | None:
    """The one committee whose date range covers today — "current" is always a
    live comparison, never a stored flag, so a committee automatically stops
    being current (and becomes a past, timeline-browsable committee) the moment
    its ``ends_at`` passes, with nothing for an admin to remember to update."""
    today = timezone.localdate()
    return (
        Committee.objects.filter(starts_at__lte=today)
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=today))
        .order_by("-starts_at")
        .first()
    )


@transaction.atomic
def create_committee(*, name: str, starts_at, ends_at, creator) -> Committee:
    name = name.strip()
    if not name:
        raise CommitteeError("Committee name is required.")
    if ends_at is not None and ends_at <= starts_at:
        raise CommitteeError("End date must be after the start date.")

    committee = Committee.objects.create(
        name=name, starts_at=starts_at, ends_at=ends_at, created_by=creator
    )

    # Auto-create the linked timeline entry so this committee is "accessible from
    # the timeline" — including after it's no longer current. Imported here (not
    # at module load) to avoid a hard import-time coupling between the two apps'
    # application layers; the models link via a string FK instead (see
    # TimelineEntry.committee).
    from apps.timeline.application.entry_service import create_entry

    create_entry(
        author=creator,
        title=name,
        description="",
        entry_date=starts_at,
        end_date=ends_at,
        image_url="",
        is_published=True,
        committee=committee,
    )

    return committee


@transaction.atomic
def set_committee_position(*, committee: Committee, user, position: str) -> CommitteeMembership:
    position = position.strip()
    if not position:
        raise CommitteeError("A position is required.")
    membership, _ = CommitteeMembership.objects.update_or_create(
        committee=committee,
        user=user,
        defaults={"position": position, "display_order": POSITION_DISPLAY_ORDER.get(position, 0)},
    )
    return membership


@transaction.atomic
def remove_committee_member(*, committee: Committee, user) -> None:
    CommitteeMembership.objects.filter(committee=committee, user=user).delete()


def get_committee_roster(*, committee: Committee, public_only: bool = False):
    queryset = (
        CommitteeMembership.objects.filter(committee=committee)
        .select_related("user", "user__profile")
        .order_by("display_order", "user__first_name")
    )
    if public_only:
        queryset = queryset.filter(user__profile__public_consent=True)
    return queryset
