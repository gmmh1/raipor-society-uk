from django.conf import settings
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel, UUIDModel


class BlogPost(UUIDModel, TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.CharField(max_length=400, blank=True)
    body = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
    )
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "blog_post"
        indexes = [
            models.Index(fields=["is_published", "published_at"]),
        ]
        ordering = ("-published_at",)

    def __str__(self) -> str:
        return self.title
