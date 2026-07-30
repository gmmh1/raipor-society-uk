from django.db import transaction

from apps.membership.models import MemberProfile


class ProfileError(ValueError):
    pass


@transaction.atomic
def get_or_create_profile_for_user(user) -> MemberProfile:
    profile, _ = MemberProfile.objects.get_or_create(user=user)
    return profile


@transaction.atomic
def update_own_profile(
    *, profile: MemberProfile, avatar_url: str, bio: str, public_consent: bool, phone_number: str
) -> MemberProfile:
    profile.avatar_url = avatar_url
    profile.bio = bio
    profile.public_consent = public_consent
    profile.save(update_fields=["avatar_url", "bio", "public_consent", "updated_at"])

    if profile.user.phone_number != phone_number:
        profile.user.phone_number = phone_number
        profile.user.save(update_fields=["phone_number"])

    return profile


@transaction.atomic
def set_position(*, profile: MemberProfile, position: str, display_order: int) -> MemberProfile:
    profile.position = position.strip()
    profile.display_order = display_order
    profile.save(update_fields=["position", "display_order", "updated_at"])
    return profile
