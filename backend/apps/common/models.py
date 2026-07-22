import uuid

from django.conf import settings
from django.db import models


class UUIDModel(models.Model):
    """Abstract base providing the UUID primary key convention used across all apps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract base providing the created/updated timestamp convention used across all apps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """Abstract base for models where deletion must preserve history for related records.

    ``objects`` excludes soft-deleted rows by default; ``all_objects`` returns everything.
    """

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["deleted_at"])

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class AuditLog(UUIDModel, TimeStampedModel):
    """Generic, cross-cutting audit trail. Any app can record an event here instead of
    hand-rolling its own narrow log table."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_log_entries",
    )
    action = models.CharField(max_length=128)
    entity_type = models.CharField(max_length=128)
    entity_id = models.CharField(max_length=64)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "common_audit_log"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action}:{self.entity_type}:{self.entity_id}"
