from django.contrib import admin

from apps.membership.models import Membership, MembershipStatusTransition


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "started_at", "ended_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")


@admin.register(MembershipStatusTransition)
class MembershipStatusTransitionAdmin(admin.ModelAdmin):
    list_display = ("id", "membership", "from_status", "to_status", "changed_by", "changed_at")
    list_filter = ("from_status", "to_status")
    search_fields = ("membership__user__username", "membership__user__email")
