from django.urls import path

from apps.media.presentation.views import ImageServeView, ImageUploadView

urlpatterns = [
    path("images/", ImageUploadView.as_view(), name="media-image-upload"),
    path("images/<str:filename>/", ImageServeView.as_view(), name="media-image-serve"),
]
