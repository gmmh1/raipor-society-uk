CHANNEL_TYPE_DIRECT = "direct"
CHANNEL_TYPE_GROUP = "group"
CHANNEL_TYPE_CHOICES = (
    (CHANNEL_TYPE_DIRECT, "Direct"),
    (CHANNEL_TYPE_GROUP, "Group"),
)

MAX_MESSAGE_LENGTH = 4000

# Roles trusted to supervise a channel that includes a minor. Deliberately narrower
# than apps.documents' STAFF_ROLES (which also includes "treasurer") — supervision is
# about people who actually interact with members, not finance access. See ADR 0016.
SUPERVISOR_ROLES = ("admin", "volunteer")
