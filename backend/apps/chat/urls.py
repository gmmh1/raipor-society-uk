from django.urls import path

from apps.chat.presentation.views import (
    ChannelMemberAddView,
    ChannelMessagesView,
    ChannelVideoCallTokenView,
    DirectChannelCreateView,
    GroupChannelCreateView,
    MessageFlagView,
    MyChannelsView,
)

urlpatterns = [
    path("channels/me/", MyChannelsView.as_view(), name="chat-channels-me"),
    path("channels/direct/", DirectChannelCreateView.as_view(), name="chat-channels-direct-create"),
    path("channels/group/", GroupChannelCreateView.as_view(), name="chat-channels-group-create"),
    path(
        "channels/<uuid:channel_id>/members/",
        ChannelMemberAddView.as_view(),
        name="chat-channels-add-member",
    ),
    path(
        "channels/<uuid:channel_id>/messages/",
        ChannelMessagesView.as_view(),
        name="chat-channels-messages",
    ),
    path(
        "channels/<uuid:channel_id>/video-token/",
        ChannelVideoCallTokenView.as_view(),
        name="chat-channels-video-token",
    ),
    path("messages/<uuid:message_id>/flag/", MessageFlagView.as_view(), name="chat-messages-flag"),
]
