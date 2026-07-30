from django.urls import path

from apps.blog.presentation.views import (
    AdminBlogPostListView,
    BlogPostDeleteView,
    BlogPostDetailView,
    BlogPostListCreateView,
    BlogPostPublishView,
)

urlpatterns = [
    path("posts/", BlogPostListCreateView.as_view(), name="blog-posts-list-create"),
    path("posts/admin/", AdminBlogPostListView.as_view(), name="blog-posts-admin-list"),
    path("posts/<slug:slug>/", BlogPostDetailView.as_view(), name="blog-posts-detail"),
    path("posts/<uuid:post_id>/publish/", BlogPostPublishView.as_view(), name="blog-posts-publish"),
    path("posts/<uuid:post_id>/delete/", BlogPostDeleteView.as_view(), name="blog-posts-delete"),
]
