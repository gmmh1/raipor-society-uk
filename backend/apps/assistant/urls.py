from django.urls import path

from apps.assistant.presentation.views import AssistantQueryView

urlpatterns = [
    path("query/", AssistantQueryView.as_view(), name="assistant-query"),
]
