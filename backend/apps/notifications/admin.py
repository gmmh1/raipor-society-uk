from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "channel", "status", "sent_at", "created_at")
    list_filter = ("channel", "status")
    search_fields = ("recipient__username", "recipient__email", "subject", "body")
