from celery import shared_task
from django.utils import timezone

from apps.finance.application.payment_service import reconciliation_summary
from apps.notifications.domain.types import CHANNEL_EMAIL

RECONCILED_CURRENCIES = ("GBP",)


@shared_task
def check_reconciliation_variance_task() -> int:
    """Daily check: alert admins/treasurers if ledger credits and succeeded payment
    transactions have drifted apart for any tracked currency. See ADR 0014.
    """
    from apps.identity.models import User
    from apps.notifications.application.notification_orchestrator import enqueue_notification

    admins = User.objects.filter(
        roles__code__in=("admin", "treasurer"), roles__is_active=True, is_active=True
    ).distinct()

    notified = 0
    for currency in RECONCILED_CURRENCIES:
        summary = reconciliation_summary(currency=currency)
        if not summary["variance_flagged"]:
            continue

        for admin_user in admins:
            enqueue_notification(
                recipient=admin_user,
                channel=CHANNEL_EMAIL,
                subject=f"Finance reconciliation variance detected ({currency})",
                body=(
                    "Ledger credit from payments: "
                    f"{summary['payment_derived_ledger_credit_minor']} minor units. "
                    "Succeeded payment transactions: "
                    f"{summary['succeeded_payment_transactions_minor']} minor units. "
                    f"Variance: {summary['variance_minor']} minor units. Please review "
                    "the reconciliation summary."
                ),
                context={"currency": currency, "variance_minor": summary["variance_minor"]},
                dedup_key=f"reconciliation-variance-{currency}-{timezone.localdate():%Y%m%d}",
            )
            notified += 1

    return notified
