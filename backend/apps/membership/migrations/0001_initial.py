# Generated manually to match `apps.membership.models` in environments where Django CLI is unavailable.

import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Membership",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="membership",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "membership_membership",
                "indexes": [
                    models.Index(fields=["status"], name="membership__status_85f6ce_idx"),
                    models.Index(fields=["created_at"], name="membership__created_157088_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="MembershipStatusTransition",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "from_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "to_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        max_length=32,
                    ),
                ),
                ("reason", models.TextField(blank=True)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="membership_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "membership",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="transitions",
                        to="membership.membership",
                    ),
                ),
            ],
            options={
                "db_table": "membership_status_transition",
                "indexes": [
                    models.Index(fields=["changed_at"], name="membership__changed_2d8fd8_idx"),
                    models.Index(
                        fields=["from_status", "to_status"],
                        name="membership__from_st_3150c8_idx",
                    ),
                ],
            },
        ),
    ]
