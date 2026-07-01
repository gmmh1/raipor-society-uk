from rest_framework import serializers

from apps.finance.domain.types import (
    DIRECTION_CHOICES,
    ENTRY_TYPE_CHOICES,
    PROVIDER_CHOICES,
)
from apps.finance.models import LedgerEntry


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


class PaymentWebhookSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=[choice[0] for choice in PROVIDER_CHOICES])
    payload = serializers.JSONField()
