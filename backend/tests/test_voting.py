from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.membership.models import MemberProfile
from apps.voting.application.poll_service import (
    VotingError,
    cast_vote,
    create_poll,
    get_results,
)
from apps.voting.models import Poll, PollBallotReceipt, PollVote


def _opts(*names):
    return [{"text": name, "image_url": ""} for name in names]


def _make_admin(username: str) -> User:
    user = User.objects.create_user(username=username, password="pass123")
    role, _ = Role.objects.get_or_create(code="admin", defaults={"name": "Admin"})
    user.roles.add(role)
    return user


def _member_with_photo(username: str) -> User:
    """Election candidates must be real members with a profile photo on file."""
    user = User.objects.create_user(username=username, password="pass123")
    MemberProfile.objects.create(user=user, avatar_url=f"https://example.com/{username}.jpg")
    return user


def _candidate_opts(*users):
    return [{"candidate_user_id": str(user.id)} for user in users]


def _open_poll(*, creator, quorum: int = 0) -> Poll:
    now = timezone.now()
    return create_poll(
        title="Committee Election",
        description="Annual vote",
        options=_opts("Alice", "Bob"),
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
        options=_opts("Yes", "No"),
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
            options=_opts("Only one"),
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
            "options": [{"text": "A"}, {"text": "B"}],
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
            "options": [{"text": "A"}, {"text": "B"}],
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
        options=_opts("Yes", "No"),
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


@pytest.mark.django_db
def test_position_election_rejects_more_than_ten_candidates():
    admin = _make_admin("poll-admin-election-1")
    now = timezone.now()
    candidates = [_member_with_photo(f"candidate1-{i}") for i in range(11)]

    with pytest.raises(VotingError, match="at most 10 candidates"):
        create_poll(
            title="Chair Election",
            description="",
            position="Chair",
            options=_candidate_opts(*candidates),
            opens_at=now,
            closes_at=now + timedelta(hours=1),
            quorum=0,
            visibility="member",
            creator=admin,
        )


@pytest.mark.django_db
def test_position_election_allows_a_single_candidate():
    admin = _make_admin("poll-admin-election-2")
    now = timezone.now()
    candidate = _member_with_photo("only-candidate")

    poll = create_poll(
        title="Uncontested Chair",
        description="",
        position="Chair",
        options=_candidate_opts(candidate),
        opens_at=now,
        closes_at=now + timedelta(hours=1),
        quorum=0,
        visibility="member",
        creator=admin,
    )

    assert poll.position == "Chair"
    assert poll.options.count() == 1
    assert poll.options.first().candidate_id == candidate.id


@pytest.mark.django_db
def test_position_election_succeeds_with_ten_candidates_and_keeps_images():
    admin = _make_admin("poll-admin-election-3")
    now = timezone.now()
    candidates = [_member_with_photo(f"candidate3-{i}") for i in range(10)]

    poll = create_poll(
        title="Secretary Election",
        description="",
        position="Secretary",
        options=_candidate_opts(*candidates),
        opens_at=now,
        closes_at=now + timedelta(hours=1),
        quorum=0,
        visibility="member",
        creator=admin,
    )

    assert poll.position == "Secretary"
    assert poll.options.count() == 10
    first_option = poll.options.first()
    assert first_option.candidate_id == candidates[0].id
    assert first_option.image_url == candidates[0].profile.avatar_url
    assert first_option.text == candidates[0].username


@pytest.mark.django_db
def test_position_election_requires_a_real_member_candidate():
    admin = _make_admin("poll-admin-election-6")
    now = timezone.now()

    with pytest.raises(VotingError, match="members list"):
        create_poll(
            title="Chair Election",
            description="",
            position="Chair",
            options=_opts("Just Some Text"),
            opens_at=now,
            closes_at=now + timedelta(hours=1),
            quorum=0,
            visibility="member",
            creator=admin,
        )


@pytest.mark.django_db
def test_position_election_rejects_candidate_without_a_photo():
    admin = _make_admin("poll-admin-election-7")
    now = timezone.now()
    photoless = User.objects.create_user(username="no-photo-yet", password="pass123")

    with pytest.raises(VotingError, match="no profile photo"):
        create_poll(
            title="Chair Election",
            description="",
            position="Chair",
            options=_candidate_opts(photoless),
            opens_at=now,
            closes_at=now + timedelta(hours=1),
            quorum=0,
            visibility="member",
            creator=admin,
        )


@pytest.mark.django_db
def test_position_election_rejects_duplicate_candidate():
    admin = _make_admin("poll-admin-election-8")
    now = timezone.now()
    candidate = _member_with_photo("double-runner")

    with pytest.raises(VotingError, match="twice"):
        create_poll(
            title="Chair Election",
            description="",
            position="Chair",
            options=_candidate_opts(candidate, candidate),
            opens_at=now,
            closes_at=now + timedelta(hours=1),
            quorum=0,
            visibility="member",
            creator=admin,
        )


@pytest.mark.django_db
def test_general_poll_still_allows_just_two_options():
    admin = _make_admin("poll-admin-election-4")
    poll = _open_poll(creator=admin)
    assert poll.position == ""
    assert poll.options.count() == 2


@pytest.mark.django_db
def test_poll_create_endpoint_enforces_election_maximum():
    admin = _make_admin("poll-admin-election-5")
    now = timezone.now()
    candidates = [_member_with_photo(f"candidate5-{i}") for i in range(11)]

    client = APIClient()
    client.force_authenticate(user=admin)

    payload = {
        "title": "Treasurer Election",
        "position": "Treasurer",
        "visibility": "member",
        "opens_at": now.isoformat(),
        "closes_at": (now + timedelta(hours=1)).isoformat(),
        "quorum": 0,
        "options": _candidate_opts(*candidates),
    }
    too_many = client.post(reverse("voting-polls-list-create"), data=payload, format="json")
    assert too_many.status_code == 400

    payload["options"] = _candidate_opts(*candidates[:10])
    ok = client.post(reverse("voting-polls-list-create"), data=payload, format="json")
    assert ok.status_code == 201
    assert ok.json()["position"] == "Treasurer"
    assert len(ok.json()["options"]) == 10


@pytest.mark.django_db
def test_poll_create_endpoint_allows_a_single_uncontested_candidate():
    admin = _make_admin("poll-admin-election-9")
    now = timezone.now()
    candidate = _member_with_photo("uncontested-api")

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        reverse("voting-polls-list-create"),
        data={
            "title": "Uncontested Vice Chair",
            "position": "Vice Chair",
            "visibility": "member",
            "opens_at": now.isoformat(),
            "closes_at": (now + timedelta(hours=1)).isoformat(),
            "quorum": 0,
            "options": _candidate_opts(candidate),
        },
        format="json",
    )
    assert response.status_code == 201
    assert len(response.json()["options"]) == 1
