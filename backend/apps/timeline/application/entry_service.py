from django.db import transaction

from apps.timeline.models import TimelineEntry


class TimelineError(ValueError):
    pass


@transaction.atomic
def create_entry(
    *, author, title: str, description: str, entry_date, image_url: str, is_published: bool
) -> TimelineEntry:
    if not title.strip():
        raise TimelineError("Title is required.")

    return TimelineEntry.objects.create(
        title=title,
        description=description,
        entry_date=entry_date,
        image_url=image_url,
        is_published=is_published,
        created_by=author,
    )


@transaction.atomic
def delete_entry(*, entry: TimelineEntry) -> TimelineEntry:
    entry.delete()  # SoftDeleteModel.delete() sets deleted_at, doesn't remove the row
    return entry
