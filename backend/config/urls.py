from django.contrib import admin
from django.urls import include, path

from apps.identity.presentation.auth_views import LoginView, LogoutView, RefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.common.urls")),
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/identity/", include("apps.identity.urls")),
    path("api/membership/", include("apps.membership.urls")),
    path("api/events/", include("apps.events.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/finance/", include("apps.finance.urls")),
    path("api/shop/", include("apps.shop.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/assistant/", include("apps.assistant.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/voting/", include("apps.voting.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
]
