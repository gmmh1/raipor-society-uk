from django.contrib import admin

from apps.chat.models import ChatChannel, ChatChannelMembership, ChatMessage


@admin.register(ChatChannel)
class ChatChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "channel_type", "created_by", "created_at")
    list_filter = ("channel_type",)
    search_fields = ("name",)


@admin.register(ChatChannelMembership)
class ChatChannelMembershipAdmin(admin.ModelAdmin):
    list_display = ("channel", "user", "created_at")
    search_fields = ("user__username",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "channel", "sender", "is_flagged", "created_at")
    list_filter = ("is_flagged",)
    search_fields = ("content", "sender__username")
