from django.db import transaction

from apps.common.audit import record_audit_event
from apps.identity.models import Role, User


class RoleAssignmentError(ValueError):
    pass


@transaction.atomic
def assign_role(*, user: User, role_code: str, actor) -> User:
    try:
        role = Role.objects.get(code=role_code, is_active=True)
    except Role.DoesNotExist as exc:
        raise RoleAssignmentError(f"Unknown or inactive role '{role_code}'.") from exc

    if user.roles.filter(pk=role.pk).exists():
        raise RoleAssignmentError(f"User already has role '{role_code}'.")

    user.roles.add(role)
    record_audit_event(
        actor=actor,
        action="role.assigned",
        entity=user,
        after={"role": role_code},
    )
    return user


@transaction.atomic
def revoke_role(*, user: User, role_code: str, actor) -> User:
    try:
        role = Role.objects.get(code=role_code)
    except Role.DoesNotExist as exc:
        raise RoleAssignmentError(f"Unknown role '{role_code}'.") from exc

    if not user.roles.filter(pk=role.pk).exists():
        raise RoleAssignmentError(f"User does not have role '{role_code}'.")

    user.roles.remove(role)
    record_audit_event(
        actor=actor,
        action="role.revoked",
        entity=user,
        before={"role": role_code},
    )
    return user
