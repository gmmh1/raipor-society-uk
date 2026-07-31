from django.db import transaction

from apps.timeline.models import TimelineEntry


class TimelineError(ValueError):
    pass


@transaction.atomic
def create_entry(
    *,
    author,
    title: str,
    description: str,
    entry_date,
    image_url: str,
    is_published: bool,
    end_date=None,
    committee=None,
) -> TimelineEntry:
    if not title.strip():
        raise TimelineError("Title is required.")
    if end_date is not None and end_date < entry_date:
        raise TimelineError("End date can't be before the start date.")

    return TimelineEntry.objects.create(
        title=title,
        description=description,
        entry_date=entry_date,
        end_date=end_date,
        image_url=image_url,
        is_published=is_published,
        created_by=author,
        committee=committee,
    )


@transaction.atomic
def delete_entry(*, entry: TimelineEntry) -> TimelineEntry:
    entry.delete()  # SoftDeleteModel.delete() sets deleted_at, doesn't remove the row
    return entry
