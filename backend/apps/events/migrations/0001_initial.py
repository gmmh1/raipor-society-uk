# Generated manually to match `apps.events.models` in environments where Django CLI is unavailable.

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
            name="Event",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("location", models.CharField(blank=True, max_length=255)),
                ("capacity", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="events_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "events_event",
                "indexes": [
                    models.Index(fields=["is_published", "starts_at"], name="events_even_is_publ_6222ec_idx"),
                    models.Index(fields=["created_at"], name="events_even_created_33a3ab_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="EventRegistration",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("registered", "Registered"),
                            ("cancelled", "Cancelled"),
                            ("attended", "Attended"),
                        ],
                        default="registered",
                        max_length=32,
                    ),
                ),
                ("qr_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("checked_in_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "checked_in_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="event_checkins_recorded",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="registrations",
                        to="events.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="event_registrations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "events_registration",
                "indexes": [models.Index(fields=["status", "created_at"], name="events_regi_status_66f175_idx")],
                "constraints": [
                    models.UniqueConstraint(fields=("event", "user"), name="unique_event_user_registration")
                ],
            },
        ),
    ]
