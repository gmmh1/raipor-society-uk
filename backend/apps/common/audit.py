from apps.common.models import AuditLog


def record_audit_event(
    *,
    actor,
    action: str,
    entity,
    before: dict | None = None,
    after: dict | None = None,
) -> AuditLog:
    """Record a cross-cutting audit event for ``entity``.

    ``entity`` must be a model instance with a ``pk``; its class name becomes ``entity_type``.
    """
    return AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        entity_type=entity.__class__.__name__,
        entity_id=str(entity.pk),
        before=before or {},
        after=after or {},
    )
