# ADR 0009: Membership Youth Safety, Dues/Tiers, and Renewal Automation

## Status

Accepted

## Context

Phase 1's gap analysis found the Youth Safety module had zero code footprint despite
minors being explicitly in scope for this charity — it exists only as marketing copy
on the web app and prose in the planning docs. This carries real GDPR (Article 8,
children's data) and UK safeguarding weight, so it was prioritized as the next slice
after Authentication rather than deferred further.

The same audit found no membership dues/tiers model at all (despite
`ENTRY_TYPE_MEMBERSHIP_FEE` already existing in `apps.finance` with nothing to produce
it) and a completely unconfigured `CELERY_BEAT_SCHEDULE` — meaning even the
Phase-3-era event-reminder Celery tasks were dead code. Both are addressed here
since they're small and one (the beat schedule) is needed to make membership expiry
automation actually run.

## Decision

### Data model

- `date_of_birth` added to `identity.User` (nullable — not collected at registration
  today; see Follow-up). `User.is_minor` is a computed property (age < 18), never
  stored, so it can't go stale.
- `apps.membership.models.GuardianRelationship`: `guardian`/`child` (both FK to
  `User`), `relationship_type`, `consent_given_at` (nullable — null means pending).
  Lives in `apps.membership`, not a new app, matching `docs/INFRASTRUCTURE_CONTINUATION_PLAN.md`'s
  grouping of "Family accounts and youth-member linking" under Identity and
  Membership, and ADR 0008's follow-up note that this is where it belongs.
- `apps.membership.models.MembershipTier` (code, name, price_minor, currency,
  billing_period_days) plus nullable `tier` FK and `expires_at` on `Membership`.

### Safeguarding gate

`transition_membership_status` (existing service, unchanged signature) now refuses to
activate a minor's membership unless at least one `GuardianRelationship` for that
child has `consent_given_at` set. This is the one concrete enforcement point the plan
calls for ("Parent/guardian approval") — it does not attempt incident logging, review
workflows, or messaging restrictions (Chat doesn't exist yet to restrict).

Consent is recorded by the guardian themselves via
`POST /api/membership/guardians/consent/` (`IsAuthenticated`, and the service rejects
the call unless `request.user` is the linked guardian) — not by an admin on their
behalf, since genuine consent has to come from the consenting party. Linking a
guardian to a child (`POST /api/membership/guardians/link/`) is admin-only, since
that's an administrative record-keeping action, not a consent action.

### Dues/tiers and renewal

`apps.membership.application.tier_service.record_dues_payment()` reuses the existing
`apps.finance.application.ledger_service.record_ledger_entry()` rather than writing a
second ledger-write path, and extends `Membership.expires_at` by the tier's
`billing_period_days` from whichever is later: now, or the current `expires_at` (so
early renewal doesn't lose remaining paid time).

A new `apps.membership.tasks.expire_memberships_task` finds `active` memberships past
their `expires_at` and transitions them to `expired` through the same (now
safeguarding-aware) `transition_membership_status`, so expiry can never bypass that
gate. `config/celery.py` now configures `CELERY_BEAT_SCHEDULE` — the first real use of
Celery beat in this project — covering this task plus the two pre-existing but
previously-unscheduled event notification tasks.

## Consequences

- A minor's membership can be created and left `pending`, but cannot be activated by
  anyone — including an admin — without the guardian consent record existing. This is
  enforced in the service layer, so every entry point (API, admin, future imports)
  gets the same guarantee.
- Recurring background jobs (membership expiry, event reminders/summaries) now
  actually run on a schedule; previously they only fired if triggered manually.
- `MembershipSerializer` now exposes `tier` and `expires_at`, a backward-compatible
  additive change to the existing `/api/membership/me/` response shape.

## Follow-up

- **Registration does not collect `date_of_birth`** — the safeguarding gate is inert
  for any user whose DOB isn't set (treated as not-minor). Collecting DOB at
  registration (or via a required profile-completion step) is necessary to make this
  gate effective in practice, not just in the data model.
- No safeguarding incident log or review workflow yet — only the activation gate.
- No self-service "child requests a guardian link" flow; linking is admin-initiated
  only.
- `django-celery-beat` (DB-backed, admin-editable schedule) was deliberately not
  added — the static `beat_schedule` dict is simpler and sufficient for three tasks;
  revisit if the schedule needs runtime editing without a deploy.
