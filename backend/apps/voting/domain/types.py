VISIBILITY_PUBLIC = "public"
VISIBILITY_MEMBER = "member"
VISIBILITY_STAFF = "staff"
VISIBILITY_CHOICES = (
    (VISIBILITY_PUBLIC, "Public"),
    (VISIBILITY_MEMBER, "Member"),
    (VISIBILITY_STAFF, "Staff"),
)

STATUS_UPCOMING = "upcoming"
STATUS_OPEN = "open"
STATUS_CLOSED = "closed"

# Who may create polls and see results early / for staff-only polls.
STAFF_ROLES = ("admin", "volunteer")

# A poll with a non-blank Poll.position (a committee-position election) can
# have at most this many candidates standing for the one position — 1 to 10.
MAX_ELECTION_CANDIDATES = 10

VOTING_METHOD_PLURALITY = "plurality"
VOTING_METHOD_RANKED_CHOICE = "ranked_choice"
VOTING_METHOD_CHOICES = (
    (VOTING_METHOD_PLURALITY, "Plurality (most votes wins)"),
    (VOTING_METHOD_RANKED_CHOICE, "Ranked-choice (instant runoff)"),
)
