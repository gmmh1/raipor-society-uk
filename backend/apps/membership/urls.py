from django.urls import path

from apps.membership.presentation.views import MembershipTransitionView, MyMembershipView

urlpatterns = [
    path("me/", MyMembershipView.as_view(), name="membership-me"),
    path("transitions/", MembershipTransitionView.as_view(), name="membership-transition"),
]
