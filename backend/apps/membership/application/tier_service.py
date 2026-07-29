from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.finance.application.ledger_service import record_ledger_entry
from apps.finance.domain.types import DIRECTION_CREDIT, ENTRY_TYPE_MEMBERSHIP_FEE
from apps.membership.models import Membership, MembershipTier


class TierError(ValueError):
    pass


@transaction.atomic
def assign_tier(*, membership: Membership, tier: MembershipTier) -> Membership:
    if not tier.is_active:
        raise TierError(f"Tier '{tier.code}' is not active.")

    membership.tier = tier
    membership.save(update_fields=["tier", "updated_at"])
    return membership


def _extend_expiry(membership: Membership, tier: MembershipTier) -> None:
    now = timezone.now()
    base = membership.expires_at if membership.expires_at and membership.expires_at > now else now
    membership.expires_at = base + timedelta(days=tier.billing_period_days)
    membership.save(update_fields=["expires_at", "updated_at"])


@transaction.atomic
def record_dues_payment(*, membership: Membership, actor, reference: str = "") -> Membership:
    if membership.tier is None:
        raise TierError("Membership has no assigned tier to bill dues against.")

    tier = membership.tier
    record_ledger_entry(
        entry_type=ENTRY_TYPE_MEMBERSHIP_FEE,
        direction=DIRECTION_CREDIT,
        amount_minor=tier.price_minor,
        currency=tier.currency,
        description=f"Membership dues: {tier.name}",
        reference=reference or str(membership.id),
        metadata={"membership_id": str(membership.id), "tier": tier.code},
        actor=actor,
    )
    _extend_expiry(membership, tier)
    return membership


def extend_membership_from_payment(*, membership_id: str) -> None:
    """Called from the finance webhook once a ``membership_fee`` checkout succeeds,
    to extend the payer's membership — without re-posting a ledger entry, since
    ``process_webhook`` already recorded one generically before calling this.
    """
    try:
        membership = Membership.objects.select_related("tier").get(id=membership_id)
    except (Membership.DoesNotExist, ValueError, ValidationError):
        return
    if membership.tier is None:
        return
    _extend_expiry(membership, membership.tier)
