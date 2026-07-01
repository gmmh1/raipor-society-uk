from django.contrib import admin

from apps.identity.models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "is_staff", "updated_at")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    filter_horizontal = ("groups", "user_permissions", "roles")
