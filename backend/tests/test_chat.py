from datetime import date, timedelta

import pytest
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.chat.application.channel_service import (
    ChatError,
    add_member,
    create_direct_channel,
    create_group_channel,
    flag_message,
    list_channel_messages,
    post_message,
)
from apps.chat.infrastructure.jwt_auth_middleware import JWTAuthMiddleware
from apps.chat.models import ChatChannel, ChatChannelMembership, ChatMessage
from apps.chat.routing import websocket_urlpatterns
from apps.identity.models import Role, User

IN_MEMORY_CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


def _minor_dob() -> date:
    return timezone.localdate() - timedelta(days=365 * 10)


def _adult_dob() -> date:
    return timezone.localdate() - timedelta(days=365 * 40)


def _make_adult(username: str) -> User:
    return User.objects.create_user(
        username=username, password="pass123", date_of_birth=_adult_dob()
    )


def _make_minor(username: str) -> User:
    return User.objects.create_user(
        username=username, password="pass123", date_of_birth=_minor_dob()
    )


def _make_supervisor(username: str) -> User:
    user = _make_adult(username)
    role, _ = Role.objects.get_or_create(code="volunteer", defaults={"name": "Volunteer"})
    user.roles.add(role)
    return user


# -- Application-layer safety rules --------------------------------------------


@pytest.mark.django_db
def test_direct_channel_between_two_adults_allowed():
    alice = _make_adult("alice-adult")
    bob = _make_adult("bob-adult")

    channel = create_direct_channel(initiator=alice, other_user=bob)

    assert ChatChannelMembership.objects.filter(channel=channel, user=alice).exists()
    assert ChatChannelMembership.objects.filter(channel=channel, user=bob).exists()


@pytest.mark.django_db
def test_direct_channel_between_two_minors_rejected():
    child_a = _make_minor("child-a")
    child_b = _make_minor("child-b")

    with pytest.raises(ChatError):
        create_direct_channel(initiator=child_a, other_user=child_b)


@pytest.mark.django_db
def test_direct_channel_minor_with_non_staff_adult_rejected():
    child = _make_minor("child-c")
    adult = _make_adult("plain-adult")

    with pytest.raises(ChatError):
        create_direct_channel(initiator=child, other_user=adult)


@pytest.mark.django_db
def test_direct_channel_minor_with_supervisor_allowed():
    child = _make_minor("child-d")
    supervisor = _make_supervisor("supervisor-1")

    channel = create_direct_channel(initiator=child, other_user=supervisor)

    assert channel.memberships.count() == 2


@pytest.mark.django_db
def test_direct_channel_is_idempotent_for_same_pair():
    alice = _make_adult("alice-dup")
    bob = _make_adult("bob-dup")

    first = create_direct_channel(initiator=alice, other_user=bob)
    second = create_direct_channel(initiator=alice, other_user=bob)

    assert first.id == second.id


@pytest.mark.django_db
def test_group_channel_with_minor_requires_supervisor():
    creator = _make_adult("creator-1")
    child = _make_minor("child-e")

    with pytest.raises(ChatError):
        create_group_channel(name="Youth Group", creator=creator, member_ids=[child.id])


@pytest.mark.django_db
def test_group_channel_with_minor_and_supervisor_allowed():
    creator = _make_supervisor("creator-2")
    child = _make_minor("child-f")

    channel = create_group_channel(name="Youth Group", creator=creator, member_ids=[child.id])

    assert channel.memberships.count() == 2


@pytest.mark.django_db
def test_add_member_introducing_unsupervised_minor_rejected():
    creator = _make_adult("creator-3")
    other = _make_adult("other-3")
    channel = create_group_channel(name="Adults Only", creator=creator, member_ids=[other.id])

    child = _make_minor("child-g")

    with pytest.raises(ChatError):
        add_member(channel=channel, user=child, actor=creator)


@pytest.mark.django_db
def test_add_member_by_non_member_rejected():
    creator = _make_adult("creator-4")
    other = _make_adult("other-4")
    channel = create_group_channel(name="Group", creator=creator, member_ids=[other.id])

    outsider = _make_adult("outsider-1")
    stranger = _make_adult("stranger-1")

    with pytest.raises(ChatError):
        add_member(channel=channel, user=stranger, actor=outsider)


@pytest.mark.django_db
def test_post_message_requires_membership():
    creator = _make_adult("creator-5")
    other = _make_adult("other-5")
    channel = create_group_channel(name="Group", creator=creator, member_ids=[other.id])

    outsider = _make_adult("outsider-2")

    with pytest.raises(ChatError):
        post_message(channel=channel, sender=outsider, content="hi")


@pytest.mark.django_db
def test_post_message_rejects_empty_content():
    creator = _make_adult("creator-6")
    other = _make_adult("other-6")
    channel = create_group_channel(name="Group", creator=creator, member_ids=[other.id])

    with pytest.raises(ChatError):
        post_message(channel=channel, sender=creator, content="   ")


@pytest.mark.django_db
def test_post_message_creates_message_and_never_deletes():
    creator = _make_adult("creator-7")
    other = _make_adult("other-7")
    channel = create_group_channel(name="Group", creator=creator, member_ids=[other.id])

    message = post_message(channel=channel, sender=creator, content="Hello everyone")

    assert ChatMessage.objects.filter(id=message.id, content="Hello everyone").exists()


@pytest.mark.django_db
def test_flag_message_marks_flagged_without_deleting():
    creator = _make_adult("creator-8")
    other = _make_adult("other-8")
    channel = create_group_channel(name="Group", creator=creator, member_ids=[other.id])
    message = post_message(channel=channel, sender=creator, content="questionable content")
    supervisor = _make_supervisor("supervisor-2")

    flagged = flag_message(message=message, actor=supervisor, reason="reported by member")

    assert flagged.is_flagged is True
    assert flagged.flagged_reason == "reported by member"
    assert ChatMessage.objects.filter(id=message.id).exists()


@pytest.mark.django_db
def test_list_channel_messages_denies_non_member_non_supervisor():
    creator = _make_adult("creator-9")
    other = _make_adult("other-9")
    channel = create_group_channel(name="Group", creator=creator, member_ids=[other.id])
    outsider = _make_adult("outsider-3")

    with pytest.raises(ChatError):
        list_channel_messages(channel=channel, user=outsider)


# -- REST API --------------------------------------------------------------------


@pytest.mark.django_db
def test_direct_channel_endpoint_requires_authentication():
    target = _make_adult("target-anon")
    client = APIClient()
    response = client.post(
        reverse("chat-channels-direct-create"), data={"user_id": str(target.id)}, format="json"
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_direct_channel_endpoint_creates_channel():
    alice = _make_adult("alice-api")
    bob = _make_adult("bob-api")

    client = APIClient()
    client.force_authenticate(user=alice)
    response = client.post(
        reverse("chat-channels-direct-create"), data={"user_id": str(bob.id)}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["channel_type"] == "direct"


@pytest.mark.django_db
def test_send_and_list_messages_via_rest():
    alice = _make_adult("alice-msg")
    bob = _make_adult("bob-msg")
    channel = create_direct_channel(initiator=alice, other_user=bob)

    client = APIClient()
    client.force_authenticate(user=alice)
    send_response = client.post(
        reverse("chat-channels-messages", kwargs={"channel_id": channel.id}),
        data={"content": "Hi Bob"},
        format="json",
    )
    assert send_response.status_code == 201

    client.force_authenticate(user=bob)
    list_url = reverse("chat-channels-messages", kwargs={"channel_id": channel.id})
    list_response = client.get(list_url)
    assert list_response.status_code == 200
    contents = [item["content"] for item in list_response.json()]
    assert "Hi Bob" in contents


@pytest.mark.django_db
def test_flag_message_endpoint_requires_supervisor_role():
    alice = _make_adult("alice-flag")
    bob = _make_adult("bob-flag")
    channel = create_direct_channel(initiator=alice, other_user=bob)
    message = post_message(channel=channel, sender=alice, content="flag me")

    client = APIClient()
    client.force_authenticate(user=bob)
    flag_url = reverse("chat-messages-flag", kwargs={"message_id": message.id})
    forbidden = client.post(flag_url)
    assert forbidden.status_code == 403

    supervisor = _make_supervisor("supervisor-3")
    client.force_authenticate(user=supervisor)
    allowed = client.post(flag_url, data={"reason": "inappropriate"}, format="json")
    assert allowed.status_code == 200
    assert allowed.json()["is_flagged"] is True


@pytest.mark.django_db
def test_my_channels_endpoint_lists_only_my_channels():
    alice = _make_adult("alice-list")
    bob = _make_adult("bob-list")
    carol = _make_adult("carol-list")

    create_direct_channel(initiator=alice, other_user=bob)
    create_direct_channel(initiator=bob, other_user=carol)

    client = APIClient()
    client.force_authenticate(user=alice)
    response = client.get(reverse("chat-channels-me"))

    assert response.status_code == 200
    assert len(response.json()) == 1


# -- WebSocket consumer -----------------------------------------------------------


@database_sync_to_async
def _acreate_adult(username: str) -> User:
    return _make_adult(username)


@database_sync_to_async
def _acreate_direct_channel(initiator: User, other_user: User) -> ChatChannel:
    return create_direct_channel(initiator=initiator, other_user=other_user)


@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=IN_MEMORY_CHANNEL_LAYERS)
def test_chat_consumer_broadcasts_message_to_both_members():
    async def run():
        alice = await _acreate_adult("alice-ws")
        bob = await _acreate_adult("bob-ws")
        channel = await _acreate_direct_channel(alice, bob)

        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        alice_token = str(AccessToken.for_user(alice))
        bob_token = str(AccessToken.for_user(bob))

        alice_url = f"/ws/chat/{channel.id}/?token={alice_token}"
        bob_url = f"/ws/chat/{channel.id}/?token={bob_token}"
        alice_comm = WebsocketCommunicator(application, alice_url)
        bob_comm = WebsocketCommunicator(application, bob_url)

        alice_connected, _ = await alice_comm.connect()
        bob_connected, _ = await bob_comm.connect()
        assert alice_connected
        assert bob_connected

        await alice_comm.send_json_to({"content": "hello via websocket"})

        bob_received = await bob_comm.receive_json_from(timeout=5)
        assert bob_received["content"] == "hello via websocket"
        assert bob_received["sender_username"] == "alice-ws"

        await alice_comm.disconnect()
        await bob_comm.disconnect()

    async_to_sync(run)()


@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=IN_MEMORY_CHANNEL_LAYERS)
def test_chat_consumer_rejects_non_member():
    async def run():
        alice = await _acreate_adult("alice-ws-2")
        bob = await _acreate_adult("bob-ws-2")
        outsider = await _acreate_adult("outsider-ws")
        channel = await _acreate_direct_channel(alice, bob)

        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        outsider_token = str(AccessToken.for_user(outsider))

        url = f"/ws/chat/{channel.id}/?token={outsider_token}"
        comm = WebsocketCommunicator(application, url)
        connected, _ = await comm.connect()
        assert connected is False

    async_to_sync(run)()
