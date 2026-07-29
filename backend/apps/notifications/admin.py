from django.contrib import admin

from apps.notifications.models import Notification, PushSubscription


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "channel", "status", "attempts", "sent_at", "created_at")
    list_filter = ("channel", "status")
    search_fields = ("recipient__username", "recipient__email", "subject", "body", "dedup_key")


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__username", "user__email", "endpoint")
