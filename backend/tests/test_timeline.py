import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.identity.models import Role, User
from apps.timeline.models import TimelineEntry


@pytest.mark.django_db
def test_timeline_list_returns_only_published_entries():
    author = User.objects.create_user(username="timeline-author-1", password="pass123")
    TimelineEntry.objects.create(
        title="Public Entry", entry_date="2020-01-01", is_published=True, created_by=author
    )
    TimelineEntry.objects.create(
        title="Draft Entry", entry_date="2020-02-01", is_published=False, created_by=author
    )

    client = APIClient()
    response = client.get(reverse("timeline-entries-list-create"))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Public Entry"


@pytest.mark.django_db
def test_timeline_create_requires_admin_or_volunteer_role():
    user = User.objects.create_user(username="timeline-plain-1", password="pass123")
    payload = {"title": "Founding", "entry_date": "2019-06-01"}

    client = APIClient()
    client.force_authenticate(user=user)
    forbidden = client.post(reverse("timeline-entries-list-create"), data=payload, format="json")
    assert forbidden.status_code == 403

    volunteer = Role.objects.create(code="volunteer", name="Volunteer")
    user.roles.add(volunteer)
    allowed = client.post(reverse("timeline-entries-list-create"), data=payload, format="json")
    assert allowed.status_code == 201
    assert allowed.json()["is_published"] is True


@pytest.mark.django_db
def test_timeline_delete_soft_deletes_and_hides_from_lists():
    author = User.objects.create_user(username="timeline-author-2", password="pass123")
    entry = TimelineEntry.objects.create(
        title="Remove Me", entry_date="2021-01-01", is_published=True, created_by=author
    )

    admin = User.objects.create_user(username="timeline-admin-1", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(reverse("timeline-entries-delete", kwargs={"entry_id": entry.id}))

    assert response.status_code == 204
    assert TimelineEntry.objects.filter(id=entry.id).count() == 0
    soft_deleted = TimelineEntry.all_objects.get(id=entry.id)
    assert soft_deleted.deleted_at is not None


@pytest.mark.django_db
def test_admin_timeline_list_includes_drafts_and_requires_role():
    author = User.objects.create_user(username="timeline-author-3", password="pass123")
    TimelineEntry.objects.create(
        title="Draft A", entry_date="2022-01-01", is_published=False, created_by=author
    )
    TimelineEntry.objects.create(
        title="Live A", entry_date="2022-02-01", is_published=True, created_by=author
    )

    plain_user = User.objects.create_user(username="timeline-plain-2", password="pass123")
    client = APIClient()
    client.force_authenticate(user=plain_user)
    forbidden = client.get(reverse("timeline-entries-admin-list"))
    assert forbidden.status_code == 403

    admin = User.objects.create_user(username="timeline-admin-2", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)
    client.force_authenticate(user=admin)
    response = client.get(reverse("timeline-entries-admin-list"))

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert titles == {"Draft A", "Live A"}
