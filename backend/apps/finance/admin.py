from django.contrib import admin

from apps.finance.models import LedgerEntry, PaymentTransaction, PaymentWebhookEvent


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "entry_type", "direction", "amount_minor", "currency", "created_at")
    list_filter = ("entry_type", "direction", "currency")
    search_fields = ("reference", "description")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "external_id", "status", "amount_minor", "currency", "updated_at")
    list_filter = ("provider", "status", "currency")
    search_fields = ("external_id",)


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "event_id", "event_type", "received_at", "processed_at")
    list_filter = ("provider",)
    search_fields = ("event_id", "event_type")
