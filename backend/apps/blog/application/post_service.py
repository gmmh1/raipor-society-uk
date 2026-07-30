from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.blog.models import BlogPost


class BlogError(ValueError):
    pass


def _unique_slug(title: str) -> str:
    base = slugify(title)[:250] or "post"
    slug = base
    suffix = 1
    while BlogPost.all_objects.filter(slug=slug).exists():
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


@transaction.atomic
def create_post(*, author, title: str, excerpt: str, body: str, cover_image_url: str, is_published: bool) -> BlogPost:
    if not title.strip():
        raise BlogError("Title is required.")

    return BlogPost.objects.create(
        title=title,
        slug=_unique_slug(title),
        excerpt=excerpt,
        body=body,
        cover_image_url=cover_image_url,
        author=author,
        is_published=is_published,
        published_at=timezone.now() if is_published else None,
    )


@transaction.atomic
def set_published(*, post: BlogPost, is_published: bool) -> BlogPost:
    if post.is_published == is_published:
        raise BlogError(f"Post is already {'published' if is_published else 'unpublished'}.")

    post.is_published = is_published
    if is_published and post.published_at is None:
        post.published_at = timezone.now()
    post.save(update_fields=["is_published", "published_at", "updated_at"])
    return post


@transaction.atomic
def delete_post(*, post: BlogPost) -> BlogPost:
    """Soft-deletes a post. See SoftDeleteModel.delete() — sets deleted_at, doesn't remove the row."""
    post.delete()
    return post
