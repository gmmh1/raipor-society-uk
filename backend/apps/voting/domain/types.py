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

# A poll with a non-blank Poll.position (a committee-position election) must
# have at least this many candidates, so voters get a real choice rather than
# a rubber-stamp of one or two names.
MIN_ELECTION_CANDIDATES = 10
