from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.chat.application.channel_service import ChatError, post_message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """One consumer instance per connected socket, scoped to a single channel.

    Membership is re-checked on connect (not cached from an earlier HTTP request),
    and every inbound message is re-validated by ``post_message`` — the same
    membership/length/youth-safety rules the REST endpoint enforces apply here too,
    since ``post_message`` is the single place those rules live.
    """

    async def connect(self):
        self.chat_channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return

        if not await self._is_member(user):
            await self.close(code=4403)
            return

        self.group_name = f"chat_{self.chat_channel_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        message_content = content.get("content", "")

        try:
            await self._post_message(user, message_content)
        except ChatError as exc:
            await self.send_json({"error": str(exc)})

    async def chat_message(self, event):
        await self.send_json(event["message"])

    @database_sync_to_async
    def _is_member(self, user) -> bool:
        from apps.chat.models import ChatChannelMembership

        return ChatChannelMembership.objects.filter(
            channel_id=self.chat_channel_id, user=user
        ).exists()

    @database_sync_to_async
    def _post_message(self, user, content):
        from apps.chat.models import ChatChannel

        channel = ChatChannel.objects.get(id=self.chat_channel_id)
        return post_message(channel=channel, sender=user, content=content)
