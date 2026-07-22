from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.identity.models import User
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.domain.types import CHANNEL_EMAIL


class PasswordResetError(ValueError):
    pass


def request_password_reset(*, email: str) -> None:
    """Silently no-ops for unknown emails to avoid leaking account existence."""
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{settings.WEB_APP_URL}/reset-password?uid={uidb64}&token={token}"

    enqueue_notification(
        recipient=user,
        channel=CHANNEL_EMAIL,
        subject="Reset your Raipor Society UK password",
        body=f"Reset your password by visiting: {reset_link}",
        context={"user_id": str(user.id)},
    )


@transaction.atomic
def confirm_password_reset(*, uidb64: str, token: str, new_password: str) -> User:
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.select_for_update().get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError) as exc:
        raise PasswordResetError("Invalid reset link.") from exc

    if not default_token_generator.check_token(user, token):
        raise PasswordResetError("Invalid or expired reset link.")

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    return user
