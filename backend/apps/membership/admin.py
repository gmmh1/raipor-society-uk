from django.contrib import admin

from apps.membership.models import (
    GuardianRelationship,
    MemberProfile,
    Membership,
    MembershipStatusTransition,
    MembershipTier,
)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "tier", "started_at", "expires_at", "updated_at")
    list_filter = ("status", "tier")
    search_fields = ("user__username", "user__email")


@admin.register(MembershipStatusTransition)
class MembershipStatusTransitionAdmin(admin.ModelAdmin):
    list_display = ("id", "membership", "from_status", "to_status", "changed_by", "changed_at")
    list_filter = ("from_status", "to_status")
    search_fields = ("membership__user__username", "membership__user__email")


@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "price_minor", "currency", "billing_period_days", "is_active")
    list_filter = ("is_active", "currency")
    search_fields = ("code", "name")


@admin.register(GuardianRelationship)
class GuardianRelationshipAdmin(admin.ModelAdmin):
    list_display = ("id", "guardian", "child", "relationship_type", "consent_given_at")
    list_filter = ("relationship_type",)
    search_fields = ("guardian__username", "child__username")


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "position", "public_consent", "display_order")
    list_filter = ("public_consent",)
    search_fields = ("user__username", "user__email", "position")
