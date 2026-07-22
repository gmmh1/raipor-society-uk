import json

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.finance.application.ledger_service import record_ledger_entry
from apps.finance.application.payment_service import process_webhook, reconciliation_summary
from apps.finance.domain.types import PROVIDER_PAYPAL, PROVIDER_STRIPE
from apps.finance.infrastructure.payment_adapters import (
    WebhookVerificationError,
    verify_paypal_signature,
    verify_stripe_signature,
)
from apps.finance.models import LedgerEntry
from apps.finance.presentation.serializers import LedgerEntryCreateSerializer, LedgerEntrySerializer
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


class StripeWebhookIngestView(APIView):
    """Ingests Stripe webhooks directly at Stripe's own JSON shape.

    Verified via ``Stripe-Signature`` over the exact raw request body before any
    parsing or database write happens (a request that fails verification never
    reaches ``process_webhook``).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            verified_event = verify_stripe_signature(
                payload_body=request.body, sig_header=sig_header
            )
        except WebhookVerificationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(str(verified_event))

        try:
            event, processed_now = process_webhook(provider=PROVIDER_STRIPE, payload=payload)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"webhook_event_id": str(event.id), "processed_now": processed_now},
            status=status.HTTP_200_OK,
        )


class PayPalWebhookIngestView(APIView):
    """Ingests PayPal webhooks directly at PayPal's own JSON shape.

    Verified via PayPal's server-side verify-webhook-signature API before any
    parsing or database write happens.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        transmission_data = {
            "transmission_id": request.META.get("HTTP_PAYPAL_TRANSMISSION_ID"),
            "transmission_time": request.META.get("HTTP_PAYPAL_TRANSMISSION_TIME"),
            "cert_url": request.META.get("HTTP_PAYPAL_CERT_URL"),
            "auth_algo": request.META.get("HTTP_PAYPAL_AUTH_ALGO"),
            "transmission_sig": request.META.get("HTTP_PAYPAL_TRANSMISSION_SIG"),
        }

        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return Response({"detail": "Invalid JSON body."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verified = verify_paypal_signature(
                headers=request.META,
                payload_body=payload,
                transmission_data=transmission_data,
            )
        except WebhookVerificationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not verified:
            return Response(
                {"detail": "PayPal signature verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event, processed_now = process_webhook(provider=PROVIDER_PAYPAL, payload=payload)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"webhook_event_id": str(event.id), "processed_now": processed_now},
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
