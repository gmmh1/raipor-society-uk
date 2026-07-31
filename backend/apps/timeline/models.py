from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel


class TimelineEntry(UUIDModel, TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    entry_date = models.DateField()
    # Set for entries spanning a period (currently: committee terms) rather than a
    # single-day milestone. Blank for ordinary one-off entries.
    end_date = models.DateField(null=True, blank=True)
    image_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="timeline_entries_created",
    )
    # String FK reference (not a Python import of apps.membership.models) — avoids
    # any import-order coupling between the two apps. Set only for auto-created
    # entries marking a committee term, so a past committee stays browsable
    # ("accessible from the timeline") after it's no longer current.
    committee = models.ForeignKey(
        "membership.Committee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="timeline_entries",
    )

    class Meta:
        db_table = "timeline_entry"
        indexes = [
            models.Index(fields=["is_published", "entry_date"]),
        ]
        ordering = ("-entry_date",)

    def __str__(self) -> str:
        return self.title
