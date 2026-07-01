from django.db import transaction

from apps.finance.models import LedgerEntry


@transaction.atomic
def record_ledger_entry(
    *,
    entry_type: str,
    direction: str,
    amount_minor: int,
    currency: str,
    description: str,
    reference: str,
    metadata: dict | None,
    actor,
) -> LedgerEntry:
    if amount_minor <= 0:
        raise ValueError("amount_minor must be greater than zero")

    return LedgerEntry.objects.create(
        entry_type=entry_type,
        direction=direction,
        amount_minor=amount_minor,
        currency=currency.upper(),
        description=description,
        reference=reference,
        metadata=metadata or {},
        recorded_by=actor,
    )
