from django.core.management.base import BaseCommand

from apps.identity.models import User
from apps.membership.application.lifecycle_service import get_or_create_membership_for_user


class Command(BaseCommand):
    """One-off backfill for users registered before self-registration started
    creating a Membership row (see registration_service.register_user). Safe
    to run more than once — get_or_create_membership_for_user is a no-op for
    users that already have one."""

    help = "Create a pending Membership row for any user that doesn't have one yet."

    def handle(self, *args, **options):
        created = 0
        for user in User.objects.filter(membership__isnull=True):
            get_or_create_membership_for_user(user)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} missing membership record(s)."))
