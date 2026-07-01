from rest_framework import serializers

from apps.identity.application.rbac_service import list_role_codes


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    email = serializers.EmailField(allow_blank=True)
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    is_active = serializers.BooleanField()
    roles = serializers.ListField(child=serializers.CharField(), read_only=True)

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "is_active": instance.is_active,
            "roles": sorted(list_role_codes(instance)),
        }


class RoleCheckRequestSerializer(serializers.Serializer):
    roles = serializers.ListField(
        child=serializers.CharField(max_length=64),
        allow_empty=False,
    )
