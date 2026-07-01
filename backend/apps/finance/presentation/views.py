from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.finance.application.ledger_service import record_ledger_entry
from apps.finance.application.payment_service import process_webhook, reconciliation_summary
from apps.finance.models import LedgerEntry
from apps.finance.presentation.serializers import (
    LedgerEntryCreateSerializer,
    LedgerEntrySerializer,
    PaymentWebhookSerializer,
)
from apps.identity.permissions import HasAnyRole


class LedgerEntryCreateView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def post(self, request):
        serializer = LedgerEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry = record_ledger_entry(
            entry_type=serializer.validated_data["entry_type"],
            direction=serializer.validated_data["direction"],
            amount_minor=serializer.validated_data["amount_minor"],
            currency=serializer.validated_data["currency"],
            description=serializer.validated_data.get("description", ""),
            reference=serializer.validated_data.get("reference", ""),
            metadata=serializer.validated_data.get("metadata", {}),
            actor=request.user,
        )

        return Response(LedgerEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class PaymentWebhookIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            event, processed_now = process_webhook(
                provider=serializer.validated_data["provider"],
                payload=serializer.validated_data["payload"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "webhook_event_id": str(event.id),
                "processed_now": processed_now,
            },
            status=status.HTTP_200_OK,
        )


class ReconciliationSummaryView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def get(self, request):
        currency = request.query_params.get("currency", "GBP")
        data = reconciliation_summary(currency=currency)
        return Response(data)


class LedgerEntryListView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def get(self, request):
        currency = request.query_params.get("currency")
        qs = LedgerEntry.objects.all().order_by("-created_at")
        if currency:
            qs = qs.filter(currency=currency.upper())
        return Response(LedgerEntrySerializer(qs, many=True).data)
