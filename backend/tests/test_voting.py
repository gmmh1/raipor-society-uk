from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.voting.application.poll_service import (
    VotingError,
    cast_vote,
    create_poll,
    get_results,
)
from apps.voting.models import Poll, PollBallotReceipt, PollVote


def _make_admin(username: str) -> User:
    user = User.objects.create_user(username=username, password="pass123")
    role, _ = Role.objects.get_or_create(code="admin", defaults={"name": "Admin"})
    user.roles.add(role)
    return user


def _open_poll(*, creator, quorum: int = 0) -> Poll:
    now = timezone.now()
    return create_poll(
        title="Committee Election",
        description="Annual vote",
        options=["Alice", "Bob"],
        opens_at=now - timedelta(hours=1),
        closes_at=now + timedelta(hours=1),
        quorum=quorum,
        visibility="member",
        creator=creator,
    )


def _closed_poll(*, creator, quorum: int = 0) -> Poll:
    now = timezone.now()
    return create_poll(
        title="Past Vote",
        description="",
        options=["Yes", "No"],
        opens_at=now - timedelta(days=2),
        closes_at=now - timedelta(days=1),
        quorum=quorum,
        visibility="member",
        creator=creator,
    )


# -- Application layer -------------------------------------------------------


@pytest.mark.django_db
def test_create_poll_requires_at_least_two_options():
    admin = _make_admin("poll-admin-1")
    with pytest.raises(VotingError):
        create_poll(
            title="Bad Poll",
            description="",
            options=["Only one"],
            opens_at=timezone.now(),
            closes_at=timezone.now() + timedelta(hours=1),
            quorum=0,
            visibility="member",
            creator=admin,
        )


@pytest.mark.django_db
def test_cast_vote_succeeds_and_creates_receipt_and_anonymous_tally():
    admin = _make_admin("poll-admin-2")
    voter = User.objects.create_user(username="voter-1", password="pass123")
    poll = _open_poll(creator=admin)
    option = poll.options.first()

    cast_vote(poll=poll, option=option, user=voter)

    assert PollBallotReceipt.objects.filter(poll=poll, user=voter).exists()
    tally = PollVote.objects.filter(poll=poll, option=option)
    assert tally.count() == 1
    # The tally row has no way to identify who cast it.
    assert not hasattr(tally.first(), "user")


@pytest.mark.django_db
def test_cast_vote_blocks_duplicate_at_database_level():
    admin = _make_admin("poll-admin-3")
    voter = User.objects.create_user(username="voter-2", password="pass123")
    poll = _open_poll(creator=admin)
    option = poll.options.first()

    cast_vote(poll=poll, option=option, user=voter)

    with pytest.raises(VotingError):
        cast_vote(poll=poll, option=poll.options.last(), user=voter)

    assert PollBallotReceipt.objects.filter(poll=poll, user=voter).count() == 1
    assert PollVote.objects.filter(poll=poll).count() == 1


@pytest.mark.django_db
def test_cast_vote_rejects_option_from_a_different_poll():
    admin = _make_admin("poll-admin-4")
    voter = User.objects.create_user(username="voter-3", password="pass123")
    poll_a = _open_poll(creator=admin)
    poll_b = _open_poll(creator=admin)

    with pytest.raises(VotingError):
        cast_vote(poll=poll_a, option=poll_b.options.first(), user=voter)


@pytest.mark.django_db
def test_cast_vote_rejects_when_poll_closed():
    admin = _make_admin("poll-admin-5")
    voter = User.objects.create_user(username="voter-4", password="pass123")
    poll = _closed_poll(creator=admin)

    with pytest.raises(VotingError):
        cast_vote(poll=poll, option=poll.options.first(), user=voter)


@pytest.mark.django_db
def test_results_hidden_before_close_for_ordinary_member():
    admin = _make_admin("poll-admin-6")
    member = User.objects.create_user(username="member-1", password="pass123")
    poll = _open_poll(creator=admin)

    with pytest.raises(VotingError):
        get_results(poll=poll, user=member)


@pytest.mark.django_db
def test_results_visible_to_staff_before_close():
    admin = _make_admin("poll-admin-7")
    poll = _open_poll(creator=admin)

    results = get_results(poll=poll, user=admin)
    assert results["status"] == "open"


@pytest.mark.django_db
def test_results_visible_to_everyone_after_close():
    admin = _make_admin("poll-admin-8")
    member = User.objects.create_user(username="member-2", password="pass123")
    poll = _closed_poll(creator=admin)

    results = get_results(poll=poll, user=member)
    assert results["status"] == "closed"


@pytest.mark.django_db
def test_quorum_met_reflects_ballot_count_not_vote_choice():
    admin = _make_admin("poll-admin-9")
    poll = _closed_poll(creator=admin, quorum=2)

    below = get_results(poll=poll, user=admin)
    assert below["quorum_met"] is False

    voter_a = User.objects.create_user(username="voter-5", password="pass123")
    voter_b = User.objects.create_user(username="voter-6", password="pass123")
    # Vote directly against the ballot receipt / tally tables since this poll is
    # already closed and cast_vote requires "open" — simulate two ballots cast
    # while it was open, then re-derive results.
    PollBallotReceipt.objects.create(poll=poll, user=voter_a)
    PollBallotReceipt.objects.create(poll=poll, user=voter_b)

    met = get_results(poll=poll, user=admin)
    assert met["quorum_met"] is True
    assert met["ballot_count"] == 2


# -- REST API ------------------------------------------------------------------


@pytest.mark.django_db
def test_poll_create_requires_staff_role():
    member = User.objects.create_user(username="member-3", password="pass123")
    client = APIClient()
    client.force_authenticate(user=member)

    response = client.post(
        reverse("voting-polls-list-create"),
        data={
            "title": "New Poll",
            "visibility": "member",
            "opens_at": timezone.now().isoformat(),
            "closes_at": (timezone.now() + timedelta(hours=1)).isoformat(),
            "quorum": 0,
            "options": ["A", "B"],
        },
        format="json",
    )
    assert response.status_code == 403

    admin = _make_admin("poll-admin-10")
    client.force_authenticate(user=admin)
    allowed = client.post(
        reverse("voting-polls-list-create"),
        data={
            "title": "New Poll",
            "visibility": "member",
            "opens_at": timezone.now().isoformat(),
            "closes_at": (timezone.now() + timedelta(hours=1)).isoformat(),
            "quorum": 0,
            "options": ["A", "B"],
        },
        format="json",
    )
    assert allowed.status_code == 201


@pytest.mark.django_db
def test_cast_vote_endpoint_and_has_voted_flag():
    admin = _make_admin("poll-admin-11")
    voter = User.objects.create_user(username="voter-7", password="pass123")
    poll = _open_poll(creator=admin)
    option_id = str(poll.options.first().id)

    client = APIClient()
    client.force_authenticate(user=voter)

    vote_response = client.post(
        reverse("voting-polls-vote", kwargs={"poll_id": poll.id}),
        data={"option_id": option_id},
        format="json",
    )
    assert vote_response.status_code == 201

    detail_response = client.get(reverse("voting-polls-detail", kwargs={"poll_id": poll.id}))
    assert detail_response.json()["has_voted"] is True

    duplicate_response = client.post(
        reverse("voting-polls-vote", kwargs={"poll_id": poll.id}),
        data={"option_id": option_id},
        format="json",
    )
    assert duplicate_response.status_code == 400


@pytest.mark.django_db
def test_results_endpoint_forbidden_before_close_for_member():
    admin = _make_admin("poll-admin-12")
    member = User.objects.create_user(username="member-4", password="pass123")
    poll = _open_poll(creator=admin)

    client = APIClient()
    client.force_authenticate(user=member)
    response = client.get(reverse("voting-polls-results", kwargs={"poll_id": poll.id}))

    assert response.status_code == 403


@pytest.mark.django_db
def test_poll_list_visibility_public_vs_member():
    admin = _make_admin("poll-admin-13")
    public_poll = create_poll(
        title="Public Poll",
        description="",
        options=["Yes", "No"],
        opens_at=timezone.now() - timedelta(hours=1),
        closes_at=timezone.now() + timedelta(hours=1),
        quorum=0,
        visibility="public",
        creator=admin,
    )
    member_poll = _open_poll(creator=admin)

    anon_response = APIClient().get(reverse("voting-polls-list-create"))
    anon_titles = {item["title"] for item in anon_response.json()}
    assert anon_titles == {public_poll.title}

    member = User.objects.create_user(username="member-5", password="pass123")
    member_client = APIClient()
    member_client.force_authenticate(user=member)
    member_response = member_client.get(reverse("voting-polls-list-create"))
    member_titles = {item["title"] for item in member_response.json()}
    assert member_titles == {public_poll.title, member_poll.title}
