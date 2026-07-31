import pyrankvote
from pyrankvote import Ballot, Candidate

from apps.voting.models import Poll, PollOption, PollRankedVote

# pyrankvote.Candidate equality/hash is based purely on its ``name`` string, not
# identity — so candidates are built from each PollOption's UUID (guaranteed unique),
# never its display text, to avoid two same-named candidates silently colliding.


def tally_ranked_choice(poll: Poll) -> dict:
    """Runs instant-runoff voting over every ranked ballot cast in this poll and
    returns a JSON-serializable round-by-round breakdown, in this project's own
    option-id terms (never pyrankvote's internal Candidate objects)."""
    options = list(PollOption.objects.filter(poll=poll).order_by("display_order"))
    option_by_key = {str(option.id): option for option in options}
    candidates = [Candidate(key) for key in option_by_key]

    ballots_by_token: dict = {}
    rows = PollRankedVote.objects.filter(poll=poll).values_list("ballot_token", "option_id", "rank")
    for ballot_token, option_id, rank in rows:
        ballots_by_token.setdefault(ballot_token, []).append((rank, str(option_id)))

    ballots = []
    for ranked_pairs in ballots_by_token.values():
        ranked_pairs.sort(key=lambda pair: pair[0])
        ballots.append(Ballot(ranked_candidates=[Candidate(key) for _, key in ranked_pairs]))

    if not ballots:
        return {"rounds": [], "winner_option_ids": [], "ballot_count": 0}

    result = pyrankvote.instant_runoff_voting(candidates, ballots)

    rounds = [
        {
            "round_number": round_number,
            "candidates": [
                {
                    "option_id": candidate_result.candidate.name,
                    "text": option_by_key[candidate_result.candidate.name].text,
                    "votes": int(round(candidate_result.number_of_votes)),
                    "status": candidate_result.status,
                }
                for candidate_result in round_result.candidate_results
            ],
        }
        for round_number, round_result in enumerate(result.rounds, start=1)
    ]

    return {
        "rounds": rounds,
        "winner_option_ids": [winner.name for winner in result.get_winners()],
        "ballot_count": len(ballots),
    }
