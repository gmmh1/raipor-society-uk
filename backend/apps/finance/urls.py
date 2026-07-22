from django.urls import path

from apps.finance.presentation.views import (
    LedgerEntryCreateView,
    LedgerEntryListView,
    PayPalWebhookIngestView,
    ReconciliationSummaryView,
    StripeWebhookIngestView,
)

urlpatterns = [
    path("ledger/entries/", LedgerEntryCreateView.as_view(), name="finance-ledger-entry-create"),
    path("ledger/", LedgerEntryListView.as_view(), name="finance-ledger-list"),
    path(
        "payments/webhooks/stripe/",
        StripeWebhookIngestView.as_view(),
        name="finance-webhook-stripe",
    ),
    path(
        "payments/webhooks/paypal/",
        PayPalWebhookIngestView.as_view(),
        name="finance-webhook-paypal",
    ),
    path(
        "reconciliation/summary/",
        ReconciliationSummaryView.as_view(),
        name="finance-reconciliation-summary",
    ),
]
