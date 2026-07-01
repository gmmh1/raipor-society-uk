from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.common.urls")),
    path("api/identity/", include("apps.identity.urls")),
    path("api/membership/", include("apps.membership.urls")),
    path("api/events/", include("apps.events.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]
