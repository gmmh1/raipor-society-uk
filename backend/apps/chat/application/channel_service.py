from django.conf import settings
from django.db import transaction

from apps.chat.application.jitsi_service import mint_jitsi_token, room_name_for_channel
from apps.chat.domain.types import (
    CHANNEL_TYPE_DIRECT,
    CHANNEL_TYPE_GROUP,
    MAX_MESSAGE_LENGTH,
    SUPERVISOR_ROLES,
)
from apps.chat.models import ChatChannel, ChatChannelMembership, ChatMessage
from apps.identity.application.rbac_service import user_has_any_role


class ChatError(ValueError):
    pass


def _is_supervisor(user) -> bool:
    return user_has_any_role(user, SUPERVISOR_ROLES)


def _assert_supervision_if_minor_present(members) -> None:
    """Youth safety gate: any set of participants that includes a minor must also
    include at least one supervisor (admin/volunteer). Applies to both channel
    creation and adding a member later — see ADR 0016.
    """
    has_minor = any(member.is_minor for member in members)
    has_supervisor = any(_is_supervisor(member) for member in members)
    if has_minor and not has_supervisor:
        raise ChatError("A channel including a minor must include at least one staff member.")


@transaction.atomic
def create_direct_channel(*, initiator, other_user) -> ChatChannel:
    if initiator.id == other_user.id:
        raise ChatError("Cannot start a direct conversation with yourself.")

    # A minor's only allowed direct-message counterpart is a supervisor — this is
    # stricter than "a minor + any adult is fine": it also blocks a minor DMing a
    # non-staff adult member, which is the safer default for a youth-serving charity.
    if initiator.is_minor and not _is_supervisor(other_user):
        raise ChatError("A minor may only start a direct conversation with a staff member.")
    if other_user.is_minor and not _is_supervisor(initiator):
        raise ChatError("A minor may only start a direct conversation with a staff member.")

    existing = (
        ChatChannel.objects.filter(channel_type=CHANNEL_TYPE_DIRECT, memberships__user=initiator)
        .filter(memberships__user=other_user)
        .distinct()
        .first()
    )
    if existing is not None:
        return existing

    channel = ChatChannel.objects.create(channel_type=CHANNEL_TYPE_DIRECT, created_by=initiator)
    ChatChannelMembership.objects.bulk_create(
        [
            ChatChannelMembership(channel=channel, user=initiator),
            ChatChannelMembership(channel=channel, user=other_user),
        ]
    )
    return channel


@transaction.atomic
def create_group_channel(*, name: str, creator, member_ids: list) -> ChatChannel:
    from apps.identity.models import User

    if not name.strip():
        raise ChatError("Group channel name is required.")

    members = list(User.objects.filter(id__in={*member_ids, creator.id}))
    if len(members) < 2:
        raise ChatError("A group channel needs at least one other member.")

    _assert_supervision_if_minor_present(members)

    channel = ChatChannel.objects.create(
        name=name.strip(), channel_type=CHANNEL_TYPE_GROUP, created_by=creator
    )
    ChatChannelMembership.objects.bulk_create(
        [ChatChannelMembership(channel=channel, user=member) for member in members]
    )
    return channel


@transaction.atomic
def add_member(*, channel: ChatChannel, user, actor) -> ChatChannelMembership:
    from apps.identity.models import User

    if channel.channel_type == CHANNEL_TYPE_DIRECT:
        raise ChatError("Cannot add members to a direct channel.")
    if not ChatChannelMembership.objects.filter(channel=channel, user=actor).exists():
        raise ChatError("Only current channel members can add new members.")
    if ChatChannelMembership.objects.filter(channel=channel, user=user).exists():
        raise ChatError("User is already a member of this channel.")

    prospective_members = list(
        User.objects.filter(chat_memberships__channel=channel)
    ) + [user]
    _assert_supervision_if_minor_present(prospective_members)

    return ChatChannelMembership.objects.create(channel=channel, user=user)


def post_message(*, channel: ChatChannel, sender, content: str) -> ChatMessage:
    content = (content or "").strip()
    if not content:
        raise ChatError("Message content cannot be empty.")
    if len(content) > MAX_MESSAGE_LENGTH:
        raise ChatError(f"Message exceeds the {MAX_MESSAGE_LENGTH}-character limit.")
    if not ChatChannelMembership.objects.filter(channel=channel, user=sender).exists():
        raise ChatError("You are not a member of this channel.")

    message = ChatMessage.objects.create(channel=channel, sender=sender, content=content)
    transaction.on_commit(lambda: _broadcast_message(message))
    return message


def _broadcast_message(message: ChatMessage) -> None:
    """Pushes a newly-created message to every WebSocket connected to its channel's
    group. A no-op if no channel layer is configured (e.g. some test contexts).
    """
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"chat_{message.channel_id}",
        {
            "type": "chat.message",
            "message": {
                "id": str(message.id),
                "channel_id": str(message.channel_id),
                "sender_id": str(message.sender_id) if message.sender_id else None,
                "sender_username": message.sender.username if message.sender_id else None,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            },
        },
    )


def flag_message(*, message: ChatMessage, actor, reason: str = "") -> ChatMessage:
    message.is_flagged = True
    message.flagged_reason = reason
    message.flagged_by = actor
    message.save(update_fields=["is_flagged", "flagged_reason", "flagged_by", "updated_at"])
    return message


def list_channel_messages(*, channel: ChatChannel, user, limit: int = 50):
    is_member = ChatChannelMembership.objects.filter(channel=channel, user=user).exists()
    if not is_member and not _is_supervisor(user):
        raise ChatError("You are not a member of this channel.")
    return channel.messages.select_related("sender").order_by("-created_at")[:limit]


def list_user_channels(*, user):
    return ChatChannel.objects.filter(memberships__user=user).distinct().order_by("-updated_at")


def create_video_call_token(*, channel: ChatChannel, user) -> dict:
    """Same channel-membership gate as messages/calls today — only a validated
    member of this channel (or a supervisor) can get a token to join its room."""
    is_member = ChatChannelMembership.objects.filter(channel=channel, user=user).exists()
    if not is_member and not _is_supervisor(user):
        raise ChatError("You are not a member of this channel.")

    room = room_name_for_channel(channel.id)
    token = mint_jitsi_token(room=room, user=user)
    return {"domain": settings.JITSI_DOMAIN, "room": room, "token": token}
