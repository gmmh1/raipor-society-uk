CHANNEL_EMAIL = "email"
CHANNEL_PUSH = "push"
CHANNEL_WHATSAPP = "whatsapp"

CHANNEL_CHOICES = (
    (CHANNEL_EMAIL, "Email"),
    (CHANNEL_PUSH, "Push"),
    (CHANNEL_WHATSAPP, "WhatsApp"),
)

STATUS_QUEUED = "queued"
STATUS_SENT = "sent"
STATUS_FAILED = "failed"

STATUS_CHOICES = (
    (STATUS_QUEUED, "Queued"),
    (STATUS_SENT, "Sent"),
    (STATUS_FAILED, "Failed"),
)
