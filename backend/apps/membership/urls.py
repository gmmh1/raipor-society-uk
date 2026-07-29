from django.urls import path

from apps.membership.presentation.views import (
    DuesRecordView,
    GuardianConsentView,
    GuardianLinkView,
    MembershipAdminListView,
    MembershipTierListCreateView,
    MembershipTransitionView,
    MyGuardianRelationshipsView,
    MyMembershipView,
    TierAssignmentView,
)

urlpatterns = [
    path("me/", MyMembershipView.as_view(), name="membership-me"),
    path("admin/", MembershipAdminListView.as_view(), name="membership-admin-list"),
    path("transitions/", MembershipTransitionView.as_view(), name="membership-transition"),
    path("guardians/link/", GuardianLinkView.as_view(), name="membership-guardians-link"),
    path("guardians/consent/", GuardianConsentView.as_view(), name="membership-guardians-consent"),
    path("guardians/me/", MyGuardianRelationshipsView.as_view(), name="membership-guardians-me"),
    path("tiers/", MembershipTierListCreateView.as_view(), name="membership-tiers"),
    path("tiers/assign/", TierAssignmentView.as_view(), name="membership-tiers-assign"),
    path("dues/record/", DuesRecordView.as_view(), name="membership-dues-record"),
]
