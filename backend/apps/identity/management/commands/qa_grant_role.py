from django.core.management.base import BaseCommand, CommandError

from apps.identity.models import Role, User


class Command(BaseCommand):
    """Utility for granting an existing role to a user by username — safe to run
    repeatedly. Useful for QA verification passes without needing a full Django
    shell session (which is awkward to invoke non-interactively over SSH)."""

    help = "Grant a role (by code) to a user (by username)."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("role_code", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        role_code = options["role_code"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"No user with username '{username}'.") from exc

        try:
            role = Role.objects.get(code=role_code)
        except Role.DoesNotExist as exc:
            raise CommandError(f"No role with code '{role_code}'.") from exc

        user.roles.add(role)
        self.stdout.write(self.style.SUCCESS(f"Granted '{role_code}' to '{username}'."))
