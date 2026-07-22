import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("raipor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "expire-memberships-daily": {
        "task": "apps.membership.tasks.expire_memberships_task",
        "schedule": crontab(hour=2, minute=0),
    },
    "enqueue-event-reminders-hourly": {
        "task": "apps.notifications.tasks.enqueue_event_reminders_task",
        "schedule": crontab(minute=0),
    },
    "enqueue-event-summaries-daily": {
        "task": "apps.notifications.tasks.enqueue_event_summary_task",
        "schedule": crontab(hour=6, minute=0),
    },
}
