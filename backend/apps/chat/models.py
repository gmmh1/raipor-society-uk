from django.conf import settings
from django.db import models

from apps.chat.domain.types import CHANNEL_TYPE_CHOICES, CHANNEL_TYPE_GROUP
from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel


class ChatChannel(UUIDModel, TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255, blank=True)
    channel_type = models.CharField(
        max_length=16, choices=CHANNEL_TYPE_CHOICES, default=CHANNEL_TYPE_GROUP
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_channels_created",
    )

    class Meta:
        db_table = "chat_channel"
        indexes = [
            models.Index(fields=["channel_type", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.name or f"{self.channel_type}:{self.id}"


class ChatChannelMembership(UUIDModel, TimeStampedModel):
    channel = models.ForeignKey(ChatChannel, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_memberships"
    )

    class Meta:
        db_table = "chat_channel_membership"
        constraints = [
            models.UniqueConstraint(fields=["channel", "user"], name="uniq_chat_channel_member"),
        ]
        indexes = [
            models.Index(fields=["user"]),
        ]


class ChatMessage(UUIDModel, TimeStampedModel):
    """Messages are never deleted or edited in place — an immutable, audit-first
    trail (same instinct as apps.assistant.AssistantInteraction and
    apps.common.AuditLog). Moderation is via ``is_flagged``, not removal.
    """

    channel = models.ForeignKey(ChatChannel, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_messages_sent",
    )
    content = models.TextField()
    is_flagged = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True)
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_messages_flagged",
    )

    class Meta:
        db_table = "chat_message"
        indexes = [
            models.Index(fields=["channel", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.channel_id}:{self.sender_id}"
