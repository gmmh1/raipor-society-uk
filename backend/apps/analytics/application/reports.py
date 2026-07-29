"""Read-only aggregation over existing modules' tables.

No new persisted entities: every report is computed live from source-of-truth
data. This is deliberate for the platform's current scale — see ADR 0018 for why
pre-aggregated/materialized reporting tables are a future consideration, not a
day-one requirement.
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone


def membership_report() -> dict:
    from apps.membership.models import Membership

    by_status = dict(
        Membership.objects.values_list("status").annotate(count=Count("id")).order_by()
    )
    return {
        "total": Membership.objects.count(),
        "by_status": by_status,
    }


def events_report() -> dict:
    from apps.events.domain.status import REG_STATUS_ATTENDED, REG_STATUS_REGISTERED
    from apps.events.models import Event, EventRegistration

    now = timezone.now()
    return {
        "total_events": Event.objects.count(),
        "upcoming_events": Event.objects.filter(starts_at__gte=now).count(),
        "total_registrations": EventRegistration.objects.count(),
        "confirmed_registrations": EventRegistration.objects.filter(
            status=REG_STATUS_REGISTERED
        ).count(),
        "attended_registrations": EventRegistration.objects.filter(
            status=REG_STATUS_ATTENDED
        ).count(),
    }


def finance_report(*, currency: str = "GBP") -> dict:
    from apps.finance.application.payment_service import reconciliation_summary
    from apps.finance.domain.types import DIRECTION_CREDIT
    from apps.finance.models import LedgerEntry

    currency = currency.upper()
    since_30_days = timezone.now() - timedelta(days=30)

    credit_total = (
        LedgerEntry.objects.filter(currency=currency, direction=DIRECTION_CREDIT)
        .aggregate(total=Sum("amount_minor"))["total"]
        or 0
    )
    credit_last_30_days = (
        LedgerEntry.objects.filter(
            currency=currency, direction=DIRECTION_CREDIT, created_at__gte=since_30_days
        ).aggregate(total=Sum("amount_minor"))["total"]
        or 0
    )
    reconciliation = reconciliation_summary(currency=currency)

    return {
        "currency": currency,
        "total_credit_minor": credit_total,
        "credit_last_30_days_minor": credit_last_30_days,
        "reconciliation_variance_flagged": reconciliation["variance_flagged"],
    }


def shop_report() -> dict:
    from apps.shop.domain.types import ORDER_FULFILLED, ORDER_PAID
    from apps.shop.models import Product, ShopOrder

    by_status = dict(
        ShopOrder.objects.values_list("status").annotate(count=Count("id")).order_by()
    )
    revenue_minor = (
        ShopOrder.objects.filter(status__in=[ORDER_PAID, ORDER_FULFILLED]).aggregate(
            total=Sum("total_minor")
        )["total"]
        or 0
    )
    return {
        "total_orders": ShopOrder.objects.count(),
        "orders_by_status": by_status,
        "revenue_minor": revenue_minor,
        "active_products": Product.objects.filter(is_active=True).count(),
    }


def documents_report() -> dict:
    from apps.documents.models import Document

    by_visibility = dict(
        Document.objects.values_list("visibility").annotate(count=Count("id")).order_by()
    )
    return {
        "total_documents": Document.objects.count(),
        "by_visibility": by_visibility,
    }


def assistant_report() -> dict:
    from apps.assistant.models import AssistantInteraction

    since_7_days = timezone.now() - timedelta(days=7)
    return {
        "total_interactions": AssistantInteraction.objects.count(),
        "interactions_last_7_days": AssistantInteraction.objects.filter(
            created_at__gte=since_7_days
        ).count(),
    }


def chat_report() -> dict:
    from apps.chat.models import ChatChannel, ChatMessage

    return {
        "total_channels": ChatChannel.objects.count(),
        "total_messages": ChatMessage.objects.count(),
        "flagged_messages": ChatMessage.objects.filter(is_flagged=True).count(),
    }


def voting_report() -> dict:
    from apps.voting.application.poll_service import poll_status
    from apps.voting.domain.types import STATUS_OPEN
    from apps.voting.models import Poll, PollBallotReceipt

    open_polls = [poll for poll in Poll.objects.all() if poll_status(poll) == STATUS_OPEN]
    return {
        "total_polls": Poll.objects.count(),
        "open_polls": len(open_polls),
        "total_ballots_cast": PollBallotReceipt.objects.count(),
    }


def overview_report() -> dict:
    return {
        "membership": membership_report(),
        "events": events_report(),
        "finance": finance_report(),
        "shop": shop_report(),
        "documents": documents_report(),
        "assistant": assistant_report(),
        "chat": chat_report(),
        "voting": voting_report(),
    }
