from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.application.reports import overview_report
from apps.identity.permissions import HasAnyRole

ANALYTICS_ROLES = ("admin", "treasurer")


class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ANALYTICS_ROLES

    def get(self, request):
        return Response(overview_report())
