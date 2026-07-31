from datetime import date

from django.db import transaction

from apps.common.models import AuditLog
from apps.documents.infrastructure.storage import StorageError, delete_object
from apps.identity.application.password_reset_service import request_password_reset
from apps.identity.domain.roles import ROLE_MEMBER
from apps.identity.models import Role, User
from apps.membership.application.lifecycle_service import get_or_create_membership_for_user
from apps.membership.application.profile_service import set_avatar_url


class MemberAdminError(ValueError):
    pass


@transaction.atomic
def create_member(
    *,
    username: str,
    email: str,
    date_of_birth: date,
    phone_number: str,
    avatar_url: str,
    first_name: str = "",
    last_name: str = "",
) -> User:
    """Admin-initiated equivalent of self-registration, for members who joined
    offline. Skips email verification (an admin is vouching for them) but still
    requires phone + photo, and sends a password-reset link so the member picks
    their own password rather than the admin choosing one for them."""
    if User.objects.filter(username=username).exists():
        raise MemberAdminError("A user with that username already exists.")
    if email and User.objects.filter(email=email).exists():
        raise MemberAdminError("A user with that email already exists.")

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        is_active=True,
    )
    user.set_unusable_password()
    user.save()

    member_role, _ = Role.objects.get_or_create(code=ROLE_MEMBER, defaults={"name": "Member"})
    user.roles.add(member_role)
    get_or_create_membership_for_user(user)
    set_avatar_url(user=user, avatar_url=avatar_url)

    if email:
        request_password_reset(email=email)

    return user


@transaction.atomic
def update_member_contact(
    *, user: User, phone_number: str | None = None, avatar_url: str | None = None
) -> User:
    if phone_number is not None and phone_number != user.phone_number:
        user.phone_number = phone_number
        user.save(update_fields=["phone_number", "updated_at"])
    if avatar_url is not None:
        set_avatar_url(user=user, avatar_url=avatar_url)
    return user


@transaction.atomic
def set_member_active(*, user: User, is_active: bool) -> User:
    user.is_active = is_active
    user.save(update_fields=["is_active", "updated_at"])
    return user


@transaction.atomic
def erase_member(*, user: User, actor: User) -> User:
    """GDPR-style erasure: scrub personally identifying data and disable the
    account, but keep the row (and everything that references it — Membership,
    ShopOrder, EventRegistration, PollBallotReceipt, financial records) intact.

    A real ``.delete()`` isn't safe on this schema: PollBallotReceipt.user and
    Documents.owner/uploaded_by use on_delete=PROTECT (deletion would simply fail
    for anyone who's voted or uploaded a document), and ShopOrder/Membership/
    EventRegistration cascade, which would destroy financial and attendance
    history this project otherwise deliberately preserves. Anonymizing in place
    satisfies "erase my personal data" without breaking either guarantee.
    """
    if user.id == actor.id:
        raise MemberAdminError("You can't erase your own account.")

    profile = getattr(user, "profile", None)
    _delete_avatar_file(getattr(profile, "avatar_url", ""))

    user.username = f"deleted-{user.id.hex[:12]}"
    user.email = ""
    user.first_name = ""
    user.last_name = ""
    user.phone_number = ""
    user.date_of_birth = None
    user.is_active = False
    user.set_unusable_password()
    user.save()

    if profile is not None:
        profile.avatar_url = ""
        profile.bio = ""
        profile.position = ""
        profile.public_consent = False
        profile.save(update_fields=["avatar_url", "bio", "position", "public_consent", "updated_at"])

    AuditLog.objects.create(
        actor=actor,
        action="member_erased",
        entity_type="User",
        entity_id=str(user.id),
    )
    return user


def _delete_avatar_file(avatar_url: str | None) -> None:
    if not avatar_url:
        return
    filename = avatar_url.rstrip("/").rsplit("/", 1)[-1]
    try:
        delete_object(key=f"images/{filename}")
    except StorageError:
        pass
