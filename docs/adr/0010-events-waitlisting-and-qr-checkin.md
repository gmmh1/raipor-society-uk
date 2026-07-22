# ADR 0010: Events Waitlisting, Self-Cancellation, and QR-Scan Check-In

## Status

Accepted

## Context

The Phase 1 gap analysis flagged two Events gaps: `EventRegistration.qr_token` was
generated and returned to clients but never actually usable — `EventCheckInView` only
accepted `registration_id`, so "QR check-in" was half-wired. Separately, reaching
event capacity just rejected further registrations outright, with no waitlist and no
promotion path, and there was no way for a member to cancel their own registration at
all (`cancelled` existed as a status value but nothing ever set it).

This was originally bundled into a larger "Phase 3: Events + Notifications +
Shop↔Finance" roadmap item, but on inspection those are three independent pieces —
Notifications' real channel adapters need a `phone_number` field on `User` that
doesn't exist yet, and Shop↔Finance needs a checkout/payment-initiation design. This
ADR covers Events only; the other two remain separate follow-up slices.

## Decision

- Added `REG_STATUS_WAITLISTED` to `apps.events.domain.status`. `register_for_event`
  now registers into `waitlisted` instead of raising when confirmed (`registered`)
  count is at capacity, reusing the same `get_or_create` + re-registration branch
  already handling cancelled→re-register.
- New `cancel_registration(registration, actor)` in
  `apps.events.application.event_service`: allowed for the registrant themselves or
  anyone with `admin`/`volunteer` (checked via the existing
  `apps.identity.application.rbac_service.user_has_any_role`, not a new permission
  class — "self OR has role" isn't expressible with the existing role-only
  `HasAnyRole`, so the check lives in the service, matching how
  `guardian_service.record_guardian_consent` self-checks actor identity in Phase 2).
  Cancelling a confirmed (`registered`) spot promotes the oldest `waitlisted`
  registration for that event and notifies them.
- `EventCheckInView` now accepts either `registration_id` or `qr_token` (exactly one,
  enforced in `EventCheckInRequestSerializer.validate()`), resolving whichever was
  provided to the same `EventRegistration` lookup. `check_in_registration` itself is
  unchanged — it still just operates on a resolved instance.
- New endpoint: `POST /api/events/registrations/<id>/cancel/`.

## Consequences

- `EventRegistration.status` gained a fourth value (`waitlisted`) — a
  choices-metadata-only migration (`0003_alter_eventregistration_status`), no column
  type change.
- Waitlist promotion is not concurrency-hardened beyond `select_for_update()` on the
  promoted row itself; the capacity check in `register_for_event` is a plain count
  query, not locked, so a burst of simultaneous registrations at the exact capacity
  boundary could over-admit by a small margin. Pre-existing behavior (the original
  capacity check had the same gap); not hardened further here to avoid scope creep.
- Volunteers scanning a physical QR code at an event door can now actually check
  someone in via `qr_token` — previously the token existed only as inert API surface.

## Follow-up

- Notifications real channel adapters (push, WhatsApp) — needs a `phone_number`
  field on `User` and, for push, a device-token model; neither exists yet.
- Shop↔Finance payment integration — needs a checkout/payment-initiation design,
  not just wiring two existing pieces together.
- Concurrency hardening on the capacity check, if event registration ever needs to
  handle high-burst simultaneous sign-ups (e.g. a popular event opening registration).
