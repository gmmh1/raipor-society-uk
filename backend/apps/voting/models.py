from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel
from apps.voting.domain.types import VISIBILITY_CHOICES, VISIBILITY_MEMBER


class Poll(UUIDModel, TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # Blank = a general poll (min 2 options). Set (e.g. "Chair", "Secretary") =
    # a committee-position election, which requires at least 10 candidates —
    # see MIN_ELECTION_CANDIDATES in application/poll_service.py.
    position = models.CharField(max_length=128, blank=True)
    visibility = models.CharField(
        max_length=16, choices=VISIBILITY_CHOICES, default=VISIBILITY_MEMBER
    )
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    quorum = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="polls_created",
    )

    class Meta:
        db_table = "voting_poll"
        indexes = [
            models.Index(fields=["visibility", "opens_at"]),
            models.Index(fields=["closes_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class PollOption(UUIDModel, TimeStampedModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    image_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    # Set only for election options (poll.position non-blank) — the member standing
    # for the position. ``text``/``image_url`` are derived from this member's own
    # profile at creation time (never trusted from the client), so the candidate
    # photo always comes from the real members list. Null for general-poll options,
    # which stay free text with no member link.
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="poll_candidacies",
    )

    class Meta:
        db_table = "voting_poll_option"
        ordering = ["display_order"]

    def __str__(self) -> str:
        return self.text


class PollBallotReceipt(UUIDModel, TimeStampedModel):
    """Proves a user cast a ballot in a poll, without recording their choice.

    The unique constraint here — not an application-level check-then-act — is what
    actually blocks duplicate voting at the database level, race-safe under
    concurrent requests. See ADR 0017.
    """

    poll = models.ForeignKey(Poll, on_delete=models.PROTECT, related_name="ballot_receipts")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="poll_ballot_receipts"
    )

    class Meta:
        db_table = "voting_poll_ballot_receipt"
        constraints = [
            models.UniqueConstraint(fields=["poll", "user"], name="uniq_poll_ballot_per_user"),
        ]
        indexes = [
            models.Index(fields=["poll"]),
        ]


class PollVote(UUIDModel, TimeStampedModel):
    """The anonymous tally record. Deliberately has no link back to a user — that
    link lives only in ``PollBallotReceipt``, which records participation but not
    choice. Nobody, including staff, can join the two to see who voted for what.
    """

    poll = models.ForeignKey(Poll, on_delete=models.PROTECT, related_name="votes")
    option = models.ForeignKey(PollOption, on_delete=models.PROTECT, related_name="votes")

    class Meta:
        db_table = "voting_poll_vote"
        indexes = [
            models.Index(fields=["poll", "option"]),
        ]
