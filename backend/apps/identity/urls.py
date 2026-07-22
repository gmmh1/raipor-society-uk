from django.urls import path

from apps.identity.views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    RoleAssignView,
    RoleRevokeView,
    VerifyEmailView,
    current_user_view,
    role_check_view,
)

urlpatterns = [
    path("me/", current_user_view, name="identity-me"),
    path("rbac/check/", role_check_view, name="identity-rbac-check"),
    path("register/", RegisterView.as_view(), name="identity-register"),
    path("verify-email/", VerifyEmailView.as_view(), name="identity-verify-email"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="identity-password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="identity-password-reset-confirm",
    ),
    path("roles/assign/", RoleAssignView.as_view(), name="identity-role-assign"),
    path("roles/revoke/", RoleRevokeView.as_view(), name="identity-role-revoke"),
]
