from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.identity.application.rbac_service import matched_roles, user_has_any_role
from apps.identity.presentation.serializers import CurrentUserSerializer, RoleCheckRequestSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    serializer = CurrentUserSerializer(request.user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def role_check_view(request):
    serializer = RoleCheckRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    required_roles = serializer.validated_data["roles"]
    return Response(
        {
            "authorized": user_has_any_role(request.user, required_roles),
            "matched_roles": matched_roles(request.user, required_roles),
        }
    )
