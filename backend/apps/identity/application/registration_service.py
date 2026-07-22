import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.identity.domain.roles import ROLE_MEMBER
from apps.identity.models import EmailVerificationToken, Role, User
from apps.notifications.application.notification_orchestrator import enqueue_notification
from apps.notifications.domain.types import CHANNEL_EMAIL

VERIFICATION_TOKEN_TTL = timedelta(hours=48)


class RegistrationError(ValueError):
    pass


@transaction.atomic
def register_user(
    *,
    username: str,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    if User.objects.filter(username=username).exists():
        raise RegistrationError("A user with that username already exists.")
    if email and User.objects.filter(email=email).exists():
        raise RegistrationError("A user with that email already exists.")

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=False,
    )
    user.set_password(password)
    user.save()

    member_role, _ = Role.objects.get_or_create(code=ROLE_MEMBER, defaults={"name": "Member"})
    user.roles.add(member_role)

    token = _issue_verification_token(user)
    verify_link = f"{settings.WEB_APP_URL}/verify-email?token={token.token}"

    enqueue_notification(
        recipient=user,
        channel=CHANNEL_EMAIL,
        subject="Verify your Raipor Society UK account",
        body=f"Welcome! Verify your email by visiting: {verify_link}",
        context={"user_id": str(user.id), "verification_token": token.token},
    )

    return user


def _issue_verification_token(user: User) -> EmailVerificationToken:
    return EmailVerificationToken.objects.create(
        user=user,
        token=secrets.token_urlsafe(32),
        expires_at=timezone.now() + VERIFICATION_TOKEN_TTL,
    )


@transaction.atomic
def verify_email(*, token: str) -> User:
    try:
        record = EmailVerificationToken.objects.select_for_update().get(token=token)
    except EmailVerificationToken.DoesNotExist as exc:
        raise RegistrationError("Invalid verification token.") from exc

    if record.consumed_at is not None:
        raise RegistrationError("This verification token has already been used.")
    if record.expires_at < timezone.now():
        raise RegistrationError("This verification token has expired.")

    record.consumed_at = timezone.now()
    record.save(update_fields=["consumed_at", "updated_at"])

    user = record.user
    user.is_active = True
    user.save(update_fields=["is_active", "updated_at"])
    return user
