import json

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.finance.application.ledger_service import record_ledger_entry
from apps.finance.application.payment_service import (
    CheckoutError,
    create_checkout_session,
    process_webhook,
    reconciliation_summary,
)
from apps.finance.application.receipt_service import (
    ReceiptError,
    get_receipt_download_url,
    issue_receipt,
)
from apps.finance.domain.types import ENTRY_TYPE_DONATION, PROVIDER_PAYPAL, PROVIDER_STRIPE
from apps.finance.infrastructure.payment_adapters import (
    WebhookVerificationError,
    verify_paypal_signature,
    verify_stripe_signature,
)
from apps.finance.models import LedgerEntry, Receipt
from apps.finance.presentation.serializers import (
    CheckoutSessionSerializer,
    CreateCheckoutSessionRequestSerializer,
    IssueReceiptRequestSerializer,
    LedgerEntryCreateSerializer,
    LedgerEntrySerializer,
    ReceiptSerializer,
)
from apps.identity.application.rbac_service import user_has_any_role
from apps.identity.models import User
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


class CreateCheckoutSessionView(APIView):
    """Initiates an outbound Stripe/PayPal payment (donation, dues, or shop sale).

    Donations are open to anonymous supporters — the public Donate page (per
    WEB_FEATURE_MATRIX.md) is the platform's primary giving surface and requiring
    an account first would kill conversion, so ``create_checkout_session`` already
    accepts ``payer=None``. Membership dues and shop sales still require a known
    account: renewing a specific membership or paying for a specific order only
    makes sense tied to an identity. See ADR 0014's Future considerations.
    """

    permission_classes = [AllowAny]
    throttle_scope = "checkout"

    def post(self, request):
        serializer = CreateCheckoutSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry_type = serializer.validated_data["entry_type"]
        if entry_type != ENTRY_TYPE_DONATION and not request.user.is_authenticated:
            return Response(
                {"detail": "Sign in required for this payment type."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            result = create_checkout_session(
                provider=serializer.validated_data["provider"],
                amount_minor=serializer.validated_data["amount_minor"],
                currency=serializer.validated_data.get("currency", "GBP"),
                entry_type=serializer.validated_data["entry_type"],
                description=serializer.validated_data.get("description", ""),
                reference=serializer.validated_data.get("reference", ""),
                payer=request.user,
                success_url=serializer.validated_data["success_url"],
                cancel_url=serializer.validated_data["cancel_url"],
            )
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CheckoutSessionSerializer(result).data, status=status.HTTP_201_CREATED)


class IssueReceiptView(APIView):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ("admin", "treasurer")

    def post(self, request):
        serializer = IssueReceiptRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ledger_entry_id = serializer.validated_data["ledger_entry_id"]
        try:
            ledger_entry = LedgerEntry.objects.get(id=ledger_entry_id)
        except LedgerEntry.DoesNotExist:
            return Response(
                {"detail": "Ledger entry not found."}, status=status.HTTP_404_NOT_FOUND
            )

        recipient = None
        recipient_id = serializer.validated_data.get("recipient_id")
        if recipient_id:
            try:
                recipient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND
                )

        try:
            receipt = issue_receipt(
                ledger_entry=ledger_entry, recipient=recipient, actor=request.user
            )
        except ReceiptError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ReceiptSerializer(receipt).data, status=status.HTTP_201_CREATED)


class MyReceiptsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        receipts = Receipt.objects.filter(recipient=request.user).order_by("-created_at")
        return Response(ReceiptSerializer(receipts, many=True).data)


class ReceiptDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, receipt_id):
        try:
            receipt = Receipt.objects.get(id=receipt_id)
        except Receipt.DoesNotExist:
            return Response({"detail": "Receipt not found."}, status=status.HTTP_404_NOT_FOUND)

        is_owner = receipt.recipient_id == request.user.id
        if not is_owner and not user_has_any_role(request.user, ("admin", "treasurer")):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response({"url": get_receipt_download_url(receipt=receipt)})
