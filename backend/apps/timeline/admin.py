from django.contrib import admin

from apps.timeline.models import TimelineEntry


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "entry_date", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "description")
