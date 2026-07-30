import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.blog.models import BlogPost
from apps.identity.models import Role, User


@pytest.mark.django_db
def test_blog_list_returns_only_published_posts():
    author = User.objects.create_user(username="author1", password="pass123")
    BlogPost.objects.create(title="Public Post", slug="public-post", is_published=True, author=author)
    BlogPost.objects.create(title="Draft Post", slug="draft-post", is_published=False, author=author)

    client = APIClient()
    response = client.get(reverse("blog-posts-list-create"))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Public Post"


@pytest.mark.django_db
def test_blog_create_requires_admin_or_volunteer_role():
    user = User.objects.create_user(username="plain-user", password="pass123")
    payload = {"title": "Role-Gated Post", "is_published": True}

    client = APIClient()
    client.force_authenticate(user=user)
    forbidden = client.post(reverse("blog-posts-list-create"), data=payload, format="json")
    assert forbidden.status_code == 403

    volunteer = Role.objects.create(code="volunteer", name="Volunteer")
    user.roles.add(volunteer)
    allowed = client.post(reverse("blog-posts-list-create"), data=payload, format="json")
    assert allowed.status_code == 201
    assert allowed.json()["slug"] == "role-gated-post"
    assert allowed.json()["published_at"] is not None


@pytest.mark.django_db
def test_blog_create_generates_unique_slug_on_title_collision():
    admin = User.objects.create_user(username="blog-admin-1", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)

    first = client.post(
        reverse("blog-posts-list-create"), data={"title": "Same Title"}, format="json"
    )
    second = client.post(
        reverse("blog-posts-list-create"), data={"title": "Same Title"}, format="json"
    )

    assert first.json()["slug"] == "same-title"
    assert second.json()["slug"] == "same-title-2"


@pytest.mark.django_db
def test_blog_detail_by_slug_hides_unpublished_posts():
    author = User.objects.create_user(username="author2", password="pass123")
    BlogPost.objects.create(title="Draft Only", slug="draft-only", is_published=False, author=author)

    client = APIClient()
    response = client.get(reverse("blog-posts-detail", kwargs={"slug": "draft-only"}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_blog_publish_toggle_requires_role_and_sets_published_at():
    author = User.objects.create_user(username="author3", password="pass123")
    post = BlogPost.objects.create(title="Toggle Me", slug="toggle-me", is_published=False, author=author)

    plain_user = User.objects.create_user(username="plain-user-2", password="pass123")
    client = APIClient()
    client.force_authenticate(user=plain_user)
    forbidden = client.post(
        reverse("blog-posts-publish", kwargs={"post_id": post.id}),
        data={"is_published": True},
        format="json",
    )
    assert forbidden.status_code == 403

    volunteer = User.objects.create_user(username="blog-volunteer", password="pass123")
    Role.objects.create(code="volunteer", name="Volunteer").users.add(volunteer)
    client.force_authenticate(user=volunteer)

    response = client.post(
        reverse("blog-posts-publish", kwargs={"post_id": post.id}),
        data={"is_published": True},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["is_published"] is True
    assert response.json()["published_at"] is not None


@pytest.mark.django_db
def test_blog_publish_toggle_rejects_no_op_transition():
    author = User.objects.create_user(username="author4", password="pass123")
    post = BlogPost.objects.create(title="Already Live", slug="already-live", is_published=True, author=author)

    admin = User.objects.create_user(username="blog-admin-2", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(
        reverse("blog-posts-publish", kwargs={"post_id": post.id}),
        data={"is_published": True},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_blog_delete_soft_deletes_and_hides_from_lists():
    author = User.objects.create_user(username="author5", password="pass123")
    post = BlogPost.objects.create(title="Remove Me", slug="remove-me", is_published=True, author=author)

    admin = User.objects.create_user(username="blog-admin-3", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.post(reverse("blog-posts-delete", kwargs={"post_id": post.id}))

    assert response.status_code == 204
    assert BlogPost.objects.filter(id=post.id).count() == 0
    soft_deleted = BlogPost.all_objects.get(id=post.id)
    assert soft_deleted.deleted_at is not None


@pytest.mark.django_db
def test_admin_blog_list_includes_drafts_and_requires_role():
    author = User.objects.create_user(username="author6", password="pass123")
    BlogPost.objects.create(title="Draft A", slug="draft-a", is_published=False, author=author)
    BlogPost.objects.create(title="Live A", slug="live-a", is_published=True, author=author)

    plain_user = User.objects.create_user(username="plain-user-3", password="pass123")
    client = APIClient()
    client.force_authenticate(user=plain_user)
    forbidden = client.get(reverse("blog-posts-admin-list"))
    assert forbidden.status_code == 403

    admin = User.objects.create_user(username="blog-admin-4", password="pass123")
    Role.objects.create(code="admin", name="Admin").users.add(admin)
    client.force_authenticate(user=admin)
    response = client.get(reverse("blog-posts-admin-list"))

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()["results"]}
    assert titles == {"Draft A", "Live A"}
