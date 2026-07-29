from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.application.channel_service import (
    ChatError,
    add_member,
    create_direct_channel,
    create_group_channel,
    flag_message,
    list_channel_messages,
    list_user_channels,
    post_message,
)
from apps.chat.domain.types import SUPERVISOR_ROLES
from apps.chat.models import ChatChannel, ChatMessage
from apps.chat.presentation.serializers import (
    AddMemberRequestSerializer,
    ChatChannelSerializer,
    ChatMessageSerializer,
    CreateDirectChannelRequestSerializer,
    CreateGroupChannelRequestSerializer,
    FlagMessageRequestSerializer,
    SendMessageRequestSerializer,
)
from apps.identity.models import User
from apps.identity.permissions import HasAnyRole


class MyChannelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        channels = list_user_channels(user=request.user)
        return Response(ChatChannelSerializer(channels, many=True).data)


class DirectChannelCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateDirectChannelRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            other_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            channel = create_direct_channel(initiator=request.user, other_user=other_user)
        except ChatError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ChatChannelSerializer(channel).data, status=status.HTTP_201_CREATED)


class GroupChannelCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateGroupChannelRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            channel = create_group_channel(
                name=serializer.validated_data["name"],
                creator=request.user,
                member_ids=serializer.validated_data["member_ids"],
            )
        except ChatError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ChatChannelSerializer(channel).data, status=status.HTTP_201_CREATED)


class ChannelMemberAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        try:
            channel = ChatChannel.objects.get(id=channel_id)
        except ChatChannel.DoesNotExist:
            return Response({"detail": "Channel not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddMemberRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            add_member(channel=channel, user=new_user, actor=request.user)
        except ChatError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class ChannelMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        try:
            channel = ChatChannel.objects.get(id=channel_id)
        except ChatChannel.DoesNotExist:
            return Response({"detail": "Channel not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            messages = list_channel_messages(channel=channel, user=request.user)
        except ChatError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(ChatMessageSerializer(messages, many=True).data)

    def post(self, request, channel_id):
        try:
            channel = ChatChannel.objects.get(id=channel_id)
        except ChatChannel.DoesNotExist:
            return Response({"detail": "Channel not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SendMessageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = post_message(
                channel=channel, sender=request.user, content=serializer.validated_data["content"]
            )
        except ChatError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)


class MessageFlagView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = SUPERVISOR_ROLES

    def post(self, request, message_id):
        try:
            message = ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            return Response({"detail": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FlagMessageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = flag_message(
            message=message, actor=request.user, reason=serializer.validated_data.get("reason", "")
        )
        return Response(ChatMessageSerializer(updated).data)
