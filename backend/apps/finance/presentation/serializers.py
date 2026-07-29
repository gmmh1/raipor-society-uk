from rest_framework import serializers

from apps.finance.domain.types import DIRECTION_CHOICES, ENTRY_TYPE_CHOICES, PROVIDER_CHOICES
from apps.finance.models import LedgerEntry, Receipt

_CHECKOUT_PROVIDER_CHOICES = [choice for choice in PROVIDER_CHOICES if choice[0] != "manual"]


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "entry_type",
            "direction",
            "amount_minor",
            "currency",
            "description",
            "reference",
            "metadata",
            "created_at",
        ]


class LedgerEntryCreateSerializer(serializers.Serializer):
    entry_type = serializers.ChoiceField(choices=[choice[0] for choice in ENTRY_TYPE_CHOICES])
    direction = serializers.ChoiceField(choices=[choice[0] for choice in DIRECTION_CHOICES])
    amount_minor = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(max_length=8, default="GBP")
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)
    reference = serializers.CharField(required=False, allow_blank=True, max_length=128)
    metadata = serializers.JSONField(required=False)


class CreateCheckoutSessionRequestSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=[choice[0] for choice in _CHECKOUT_PROVIDER_CHOICES])
    entry_type = serializers.ChoiceField(choices=[choice[0] for choice in ENTRY_TYPE_CHOICES])
    amount_minor = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(max_length=8, default="GBP")
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)
    reference = serializers.CharField(required=False, allow_blank=True, max_length=128)
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class CheckoutSessionSerializer(serializers.Serializer):
    provider = serializers.CharField()
    external_id = serializers.CharField()
    redirect_url = serializers.CharField()


class ReceiptSerializer(serializers.ModelSerializer):
    ledger_entry_id = serializers.UUIDField(source="ledger_entry.id", read_only=True)
    recipient_id = serializers.UUIDField(source="recipient.id", read_only=True, allow_null=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "receipt_number",
            "ledger_entry_id",
            "recipient_id",
            "amount_minor",
            "currency",
            "description",
            "created_at",
        ]


class IssueReceiptRequestSerializer(serializers.Serializer):
    ledger_entry_id = serializers.UUIDField()
    recipient_id = serializers.UUIDField(required=False)
