# Generated manually to match `apps.notifications.models` in environments where Django CLI is unavailable.

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
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "channel",
                    models.CharField(
                        choices=[("email", "Email"), ("push", "Push"), ("whatsapp", "WhatsApp")],
                        max_length=32,
                    ),
                ),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField()),
                ("context", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed")],
                        default="queued",
                        max_length=32,
                    ),
                ),
                ("error_message", models.TextField(blank=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "recipient",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "notifications_notification",
                "indexes": [
                    models.Index(fields=["status", "created_at"], name="notificatio_status_4ff4fc_idx"),
                    models.Index(fields=["channel"], name="notificatio_channel_4cba03_idx"),
                ],
            },
        ),
    ]
