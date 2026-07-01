from rest_framework.permissions import BasePermission

from apps.identity.application.rbac_service import user_has_any_role


class HasAnyRole(BasePermission):
    """Permission that checks `view.required_roles` against the authenticated user."""

    message = "You do not have one of the required roles to perform this action."

    def has_permission(self, request, view) -> bool:
        required_roles = getattr(view, "required_roles", None)
        if not request.user.is_authenticated or not required_roles:
            return False
        return user_has_any_role(request.user, required_roles)
