from django.urls import path

from apps.finance.presentation.views import (
    LedgerEntryCreateView,
    LedgerEntryListView,
    PaymentWebhookIngestView,
    ReconciliationSummaryView,
)

urlpatterns = [
    path("ledger/entries/", LedgerEntryCreateView.as_view(), name="finance-ledger-entry-create"),
    path("ledger/", LedgerEntryListView.as_view(), name="finance-ledger-list"),
    path("payments/webhooks/", PaymentWebhookIngestView.as_view(), name="finance-payment-webhook-ingest"),
    path("reconciliation/summary/", ReconciliationSummaryView.as_view(), name="finance-reconciliation-summary"),
]
