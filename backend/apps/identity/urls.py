from django.urls import path

from apps.identity.views import current_user_view, role_check_view

urlpatterns = [
    path("me/", current_user_view, name="identity-me"),
    path("rbac/check/", role_check_view, name="identity-rbac-check"),
]
