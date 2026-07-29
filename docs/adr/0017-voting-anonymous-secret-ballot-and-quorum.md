# ADR 0017: Voting — Anonymous Secret Ballot, Duplicate Prevention, and Quorum

## Status

Accepted

## Context

Module 11 (Voting) is next in the build order. `CLAUDE.md`'s Phase 6 acceptance
criteria are explicit and unusually strict for this codebase: "duplicate voting
blocked at database level" (not just an application-level check) and "vote
tampering protection via immutable audit records," on top of the deliverable
itself requiring anonymity and quorum. Anonymity and duplicate-prevention are in
tension — you need to know *who* voted to stop them voting twice, but not know
*what* they voted for.

## Decision

New bounded context `apps.voting`, built around a deliberate split between
participation and choice:

- `Poll`: title, description, three-tier `visibility` (public/member/staff, same
  shape as `apps.documents`), `opens_at`/`closes_at` (status — `upcoming`/`open`/
  `closed` — is derived from these timestamps, not a separately-managed field, so
  there's no way for status and time to disagree), and `quorum` (minimum ballot
  count for the result to be considered valid).
- `PollOption`: the choices for a poll.
- `PollBallotReceipt`: proves a specific user cast a ballot in a specific poll —
  **and nothing else**. `UniqueConstraint(fields=["poll", "user"])` is what
  actually blocks duplicate voting at the database level: `cast_vote` doesn't
  check-then-create (a race condition under concurrent requests); it always
  attempts the `create()` inside a nested `transaction.atomic()` savepoint and
  catches `IntegrityError`, converting a constraint violation into a
  `VotingError`. This is race-safe by construction, not by application-level
  discipline.
- `PollVote`: the actual tally record — `poll`, `option`, and **no FK to `user`
  at all**. This is what makes voting genuinely anonymous rather than
  "anonymous but technically traceable by an admin with database access": the
  link between a person and their choice simply does not exist anywhere in the
  schema. `PollBallotReceipt` and `PollVote` are created together in
  `cast_vote`, but nothing connects one specific receipt row to one specific
  vote row.
- Both `PollBallotReceipt` and `PollVote` use `on_delete=models.PROTECT` on their
  `poll` FK (and `PollBallotReceipt` on `user` too) — an immutable audit trail
  per the acceptance criterion; nothing about a poll's ballot or vote history can
  be cascaded away.
- **Results visibility**: hidden from ordinary members until a poll closes
  (`get_results` raises `VotingError` otherwise), visible to staff
  (`admin`/`volunteer`) at any time — mid-poll visibility for ordinary members
  creates a bandwagon/tampering incentive; staff need it earlier to judge
  turnout against quorum before deciding whether to extend voting.
- `quorum_met` is `ballot_count >= poll.quorum` — counted from
  `PollBallotReceipt`, never from `PollVote` (counting votes instead would still
  work numerically since it's 1:1, but conceptually quorum is about
  *participation*, which is what the receipt table represents).

API: `GET/POST /api/voting/polls/` (create is staff-only), `GET
/api/voting/polls/{id}/`, `POST /api/voting/polls/{id}/vote/`, `GET
/api/voting/polls/{id}/results/`.

## Consequences

- Nobody — not even a database administrator — can determine how a specific
  member voted, short of correlating `PollBallotReceipt.created_at` with
  `PollVote.created_at` timing, which is not a link the schema itself provides.
- Duplicate votes are impossible under concurrent load, not just impossible in
  the happy path — verified by a test that the second `cast_vote` call for the
  same user/poll raises rather than silently succeeding or racing.
- A poll's history (who participated, what the tally was) can never be deleted
  once any vote exists, by construction of `PROTECT`.

## Future considerations

- Voting eligibility today is "any authenticated user who can see the poll"
  (gated by `visibility`, same as viewing). It does **not** check membership
  status (e.g. requiring an `active` `Membership` — ADR 0003/0009). If real
  governance votes need "only paid-up members may vote," that's a follow-up
  eligibility check in `cast_vote`, deliberately not added now to avoid coupling
  this module to membership-status business rules the acceptance criteria didn't
  ask for.
- No way to close a poll early — `closes_at` is fixed at creation. A real
  governance process might need a chair to end voting ahead of schedule.
- No public list of *who* participated (only staff can see `PollBallotReceipt`
  via the admin) — could be exposed via an API for transparency
  ("42 of 60 members voted") without touching anonymity, if that's wanted later.
