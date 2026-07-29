from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistant.application.assistant_service import answer_question
from apps.assistant.presentation.serializers import (
    AssistantAnswerSerializer,
    AssistantQuerySerializer,
)


class AssistantQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssistantQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = answer_question(
            user=request.user, question=serializer.validated_data["question"]
        )
        return Response(AssistantAnswerSerializer(result).data)
