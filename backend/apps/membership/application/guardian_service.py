from django.db import transaction
from django.utils import timezone

from apps.common.audit import record_audit_event
from apps.membership.models import GuardianRelationship


class GuardianRelationshipError(ValueError):
    pass


@transaction.atomic
def link_guardian(*, guardian, child, relationship_type: str, actor) -> GuardianRelationship:
    if guardian.pk == child.pk:
        raise GuardianRelationshipError("A user cannot be their own guardian.")

    if GuardianRelationship.objects.filter(guardian=guardian, child=child).exists():
        raise GuardianRelationshipError("This guardian relationship already exists.")

    relationship = GuardianRelationship.objects.create(
        guardian=guardian,
        child=child,
        relationship_type=relationship_type,
    )
    record_audit_event(
        actor=actor,
        action="guardian.linked",
        entity=relationship,
        after={"guardian": str(guardian.id), "child": str(child.id)},
    )
    return relationship


@transaction.atomic
def record_guardian_consent(*, relationship: GuardianRelationship, actor) -> GuardianRelationship:
    if actor.pk != relationship.guardian_id:
        raise GuardianRelationshipError("Only the linked guardian can record consent.")

    if relationship.consent_given_at is not None:
        raise GuardianRelationshipError("Consent has already been recorded for this relationship.")

    relationship.consent_given_at = timezone.now()
    relationship.save(update_fields=["consent_given_at", "updated_at"])

    record_audit_event(
        actor=actor,
        action="guardian.consent_recorded",
        entity=relationship,
        after={"consent_given_at": relationship.consent_given_at.isoformat()},
    )
    return relationship


def has_active_consent(*, child) -> bool:
    return GuardianRelationship.objects.filter(child=child, consent_given_at__isnull=False).exists()
