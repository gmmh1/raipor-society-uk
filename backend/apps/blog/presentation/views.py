from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blog.application.post_service import BlogError, create_post, delete_post, set_published
from apps.blog.models import BlogPost
from apps.blog.presentation.serializers import (
    BlogPostCreateSerializer,
    BlogPostPublishSerializer,
    BlogPostSerializer,
)
from apps.common.pagination import StandardResultsPagination
from apps.identity.permissions import HasAnyRole


class BlogPostListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            self.required_roles = ("admin", "volunteer")
            return [IsAuthenticated(), HasAnyRole()]
        return [AllowAny()]

    def get(self, _request):
        posts = BlogPost.objects.filter(is_published=True).order_by("-published_at")
        return Response(BlogPostSerializer(posts, many=True).data)

    def post(self, request):
        serializer = BlogPostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            post = create_post(author=request.user, **serializer.validated_data)
        except BlogError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(BlogPostSerializer(post).data, status=status.HTTP_201_CREATED)


class BlogPostDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, slug):
        try:
            post = BlogPost.objects.get(slug=slug, is_published=True)
        except BlogPost.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(BlogPostSerializer(post).data)


class AdminBlogPostListView(APIView):
    """All posts, published or draft, for the blog admin screen —
    distinct from the public list, which only ever returns published posts."""

    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def get(self, request):
        posts = BlogPost.objects.select_related("author").order_by("-created_at")
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = BlogPostSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BlogPostPublishView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def post(self, request, post_id):
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BlogPostPublishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated = set_published(post=post, is_published=serializer.validated_data["is_published"])
        except BlogError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(BlogPostSerializer(updated).data)


class BlogPostDeleteView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "volunteer")

    def post(self, _request, post_id):
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        delete_post(post=post)
        return Response(status=status.HTTP_204_NO_CONTENT)
