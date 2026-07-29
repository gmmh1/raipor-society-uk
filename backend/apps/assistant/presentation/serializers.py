from rest_framework import serializers


class AssistantQuerySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)


class AssistantCitationSerializer(serializers.Serializer):
    document_id = serializers.UUIDField()
    document_title = serializers.CharField()
    version_id = serializers.UUIDField()
    chunk_id = serializers.UUIDField()


class AssistantAnswerSerializer(serializers.Serializer):
    answer = serializers.CharField()
    citations = AssistantCitationSerializer(many=True)
