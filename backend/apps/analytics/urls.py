from django.urls import path

from apps.analytics.presentation.views import AnalyticsOverviewView

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view(), name="analytics-overview"),
]
