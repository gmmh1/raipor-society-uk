from django.urls import path

from apps.finance.presentation.views import (
    CreateCheckoutSessionView,
    IssueReceiptView,
    LedgerEntryCreateView,
    LedgerEntryListView,
    MyReceiptsView,
    PayPalWebhookIngestView,
    ReceiptDownloadView,
    ReconciliationSummaryView,
    StripeWebhookIngestView,
)

urlpatterns = [
    path("ledger/entries/", LedgerEntryCreateView.as_view(), name="finance-ledger-entry-create"),
    path("ledger/", LedgerEntryListView.as_view(), name="finance-ledger-list"),
    path(
        "payments/checkout/",
        CreateCheckoutSessionView.as_view(),
        name="finance-payments-checkout",
    ),
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
    path("receipts/", IssueReceiptView.as_view(), name="finance-receipts-issue"),
    path("receipts/me/", MyReceiptsView.as_view(), name="finance-receipts-me"),
    path(
        "receipts/<uuid:receipt_id>/download/",
        ReceiptDownloadView.as_view(),
        name="finance-receipts-download",
    ),
]
