from rest_framework import serializers

from apps.blog.models import BlogPost


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "body",
            "cover_image_url",
            "author_name",
            "is_published",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "published_at", "created_at", "updated_at"]

    def get_author_name(self, post: BlogPost) -> str:
        if not post.author_id:
            return ""
        return (f"{post.author.first_name} {post.author.last_name}".strip()) or post.author.username


class BlogPostCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    excerpt = serializers.CharField(max_length=400, required=False, allow_blank=True, default="")
    body = serializers.CharField(required=False, allow_blank=True, default="")
    cover_image_url = serializers.URLField(required=False, allow_blank=True, default="")
    is_published = serializers.BooleanField(required=False, default=False)


class BlogPostPublishSerializer(serializers.Serializer):
    is_published = serializers.BooleanField()
