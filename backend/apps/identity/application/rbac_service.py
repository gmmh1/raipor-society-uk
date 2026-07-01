from collections.abc import Iterable

from django.contrib.auth import get_user_model

User = get_user_model()


def list_role_codes(user: User) -> set[str]:
    if not user.is_authenticated:
        return set()
    return set(user.roles.filter(is_active=True).values_list("code", flat=True))


def user_has_any_role(user: User, required_roles: Iterable[str]) -> bool:
    required = {role.strip() for role in required_roles if role and role.strip()}
    if not required:
        return False
    return bool(required.intersection(list_role_codes(user)))


def matched_roles(user: User, required_roles: Iterable[str]) -> list[str]:
    required = {role.strip() for role in required_roles if role and role.strip()}
    current = list_role_codes(user)
    return sorted(required.intersection(current))
