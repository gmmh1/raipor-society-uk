from django.db import IntegrityError, transaction
from django.db.models import Count, QuerySet
from django.utils import timezone

from apps.identity.application.rbac_service import user_has_any_role
from apps.voting.domain.types import (
    MIN_ELECTION_CANDIDATES,
    STAFF_ROLES,
    STATUS_CLOSED,
    STATUS_OPEN,
    STATUS_UPCOMING,
    VISIBILITY_MEMBER,
    VISIBILITY_PUBLIC,
)
from apps.voting.models import Poll, PollBallotReceipt, PollOption, PollVote


class VotingError(ValueError):
    pass


def visible_polls_queryset(user) -> QuerySet[Poll]:
    base = Poll.objects.all()
    if not user or not user.is_authenticated:
        return base.filter(visibility=VISIBILITY_PUBLIC)
    if user_has_any_role(user, STAFF_ROLES):
        return base
    return base.filter(visibility__in=[VISIBILITY_PUBLIC, VISIBILITY_MEMBER])


def get_visible_poll(*, user, poll_id) -> Poll | None:
    return visible_polls_queryset(user).filter(id=poll_id).first()


@transaction.atomic
def create_poll(
    *,
    title: str,
    description: str,
    options: list[dict],
    opens_at,
    closes_at,
    quorum: int,
    visibility: str,
    creator,
    position: str = "",
) -> Poll:
    if not title.strip():
        raise VotingError("Title is required.")
    cleaned_options = [
        {"text": option["text"].strip(), "image_url": option.get("image_url", "")}
        for option in options
        if option["text"].strip()
    ]
    position = position.strip()

    if position and len(cleaned_options) < MIN_ELECTION_CANDIDATES:
        raise VotingError(
            f"A position election needs at least {MIN_ELECTION_CANDIDATES} candidates."
        )
    if not position and len(cleaned_options) < 2:
        raise VotingError("A poll needs at least two non-empty options.")
    if closes_at <= opens_at:
        raise VotingError("closes_at must be after opens_at.")

    poll = Poll.objects.create(
        title=title.strip(),
        description=description,
        position=position,
        visibility=visibility,
        opens_at=opens_at,
        closes_at=closes_at,
        quorum=quorum,
        created_by=creator,
    )
    PollOption.objects.bulk_create(
        [
            PollOption(
                poll=poll,
                text=option["text"],
                image_url=option["image_url"],
                display_order=index,
            )
            for index, option in enumerate(cleaned_options)
        ]
    )
    return poll


def poll_status(poll: Poll) -> str:
    now = timezone.now()
    if now < poll.opens_at:
        return STATUS_UPCOMING
    if now < poll.closes_at:
        return STATUS_OPEN
    return STATUS_CLOSED


@transaction.atomic
def cast_vote(*, poll: Poll, option: PollOption, user) -> None:
    if option.poll_id != poll.id:
        raise VotingError("Option does not belong to this poll.")
    if poll_status(poll) != STATUS_OPEN:
        raise VotingError("This poll is not currently open for voting.")

    try:
        with transaction.atomic():
            PollBallotReceipt.objects.create(poll=poll, user=user)
    except IntegrityError as exc:
        raise VotingError("You have already voted in this poll.") from exc

    # No FK to ``user`` here — this row is the anonymous tally, not the receipt.
    PollVote.objects.create(poll=poll, option=option)


def has_user_voted(*, poll: Poll, user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    return PollBallotReceipt.objects.filter(poll=poll, user=user).exists()


def get_results(*, poll: Poll, user) -> dict:
    """Results are hidden from ordinary members until the poll closes — seeing a
    running tally mid-vote creates a bandwagon/tampering incentive. Staff can
    check anytime, e.g. to monitor turnout against quorum before closing.
    """
    if poll_status(poll) != STATUS_CLOSED and not user_has_any_role(user, STAFF_ROLES):
        raise VotingError("Results are not available until the poll closes.")

    tallies = (
        PollOption.objects.filter(poll=poll)
        .annotate(vote_count=Count("votes"))
        .order_by("display_order")
    )
    ballot_count = PollBallotReceipt.objects.filter(poll=poll).count()

    return {
        "poll_id": str(poll.id),
        "status": poll_status(poll),
        "ballot_count": ballot_count,
        "quorum": poll.quorum,
        "quorum_met": ballot_count >= poll.quorum,
        "options": [
            {
                "id": str(option.id),
                "text": option.text,
                "image_url": option.image_url,
                "vote_count": option.vote_count,
            }
            for option in tallies
        ],
    }
