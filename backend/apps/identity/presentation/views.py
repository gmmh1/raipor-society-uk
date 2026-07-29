from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.application.password_reset_service import (
    PasswordResetError,
    confirm_password_reset,
    request_password_reset,
)
from apps.identity.application.rbac_service import matched_roles, user_has_any_role
from apps.identity.application.registration_service import (
    RegistrationError,
    register_user,
    verify_email,
)
from apps.identity.application.role_assignment_service import (
    RoleAssignmentError,
    assign_role,
    revoke_role,
)
from apps.identity.models import User
from apps.identity.permissions import HasAnyRole
from apps.identity.presentation.serializers import (
    CurrentUserSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterRequestSerializer,
    RoleAssignmentRequestSerializer,
    RoleCheckRequestSerializer,
    UpdateProfileRequestSerializer,
    VerifyEmailRequestSerializer,
)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    if request.method == "PATCH":
        serializer = UpdateProfileRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(request.user, field, value)
        if serializer.validated_data:
            request.user.save(update_fields=[*serializer.validated_data.keys(), "updated_at"])

    return Response(CurrentUserSerializer(request.user).data)


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


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = register_user(**serializer.validated_data)
        except RegistrationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"id": str(user.id), "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = verify_email(token=serializer.validated_data["token"])
        except RegistrationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"id": str(user.id), "is_active": user.is_active})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_password_reset(email=serializer.validated_data["email"])
        # Always 202: never reveal whether the email is a registered account.
        return Response(status=status.HTTP_202_ACCEPTED)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            confirm_password_reset(
                uidb64=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )
        except PasswordResetError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class RoleAssignView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = RoleAssignmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            target_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            assign_role(
                user=target_user,
                role_code=serializer.validated_data["role_code"],
                actor=request.user,
            )
        except RoleAssignmentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CurrentUserSerializer(target_user).data)


class RoleRevokeView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin",)

    def post(self, request):
        serializer = RoleAssignmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            target_user = User.objects.get(id=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            revoke_role(
                user=target_user,
                role_code=serializer.validated_data["role_code"],
                actor=request.user,
            )
        except RoleAssignmentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CurrentUserSerializer(target_user).data)
