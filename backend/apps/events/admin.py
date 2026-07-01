from django.contrib import admin

from apps.events.models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "starts_at", "ends_at", "is_published", "capacity")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "location")


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "status", "checked_in_at")
    list_filter = ("status",)
    search_fields = ("event__title", "user__username", "user__email")
