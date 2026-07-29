# ADR 0016: Chat — Real-Time Channels and Youth Safety Constraints

## Status

Accepted

## Context

Module 10 (Chat) is next in the build order. Per `CLAUDE.md`, this platform serves a
membership that includes minors (the safeguarding gate on membership activation —
ADR 0009 — already establishes `identity.User.is_minor` and a guardian/consent
model), and the tech stack commits to Django Channels for real-time features. This
is the first module in the codebase that needs a persistent bidirectional
connection rather than request/response, and the first to need any kind of content
moderation.

## Decision

New bounded context `apps.chat`:

- `ChatChannel` (`direct` or `group`, soft-deletable), `ChatChannelMembership`
  (one row per member), `ChatMessage` (immutable — no edit/delete, only an
  `is_flagged` moderation flag with `flagged_reason`/`flagged_by`). This mirrors
  the audit-first instinct already established by `apps.common.AuditLog` and
  `apps.assistant.AssistantInteraction`: messages sent to or by a minor must stay
  reviewable, not disappear.

**Youth safety rules**, enforced in `apps.chat.application.channel_service` (not
just at the presentation layer, so the WebSocket consumer and the REST API can't
diverge):

- A minor's only allowed **direct-message** counterpart is a supervisor
  (`SUPERVISOR_ROLES = ("admin", "volunteer")` — narrower than `apps.documents`'
  `STAFF_ROLES`, which also includes `treasurer`; supervision is about people who
  actually interact with members, not finance access). This blocks minor↔minor DMs
  *and* minor↔ordinary-adult-member DMs — the safer default, not just "block
  minor-to-minor."
- Any **group channel** containing a minor must contain at least one supervisor
  among its members, checked both at creation and whenever a member is later
  added (`add_member` re-checks the resulting membership set, not just the
  incoming user).
- Every message is permanently retained; moderation is "flag for review"
  (supervisor-only), never deletion.

**Real-time transport**: `channels` + `channels_redis` (Redis-backed channel
layer, reusing the same Redis already in `docker-compose.yml` — no new
infrastructure dependency) + `daphne` as the ASGI server (Channels' own,
pure-Python, matching the "avoid vendor lock-in" preference over e.g. a hosted
WebSocket service). `ChatConsumer` re-validates channel membership on `connect`
(not trusted from an earlier HTTP call) and every inbound message goes through
the *same* `post_message` application function the REST endpoint uses — the
youth-safety and membership checks live in exactly one place regardless of which
transport a client used to send a message.

**WebSocket authentication**: Channels' built-in `AuthMiddlewareStack` only
understands Django sessions, but this platform's REST API authenticates via JWT
(`djangorestframework-simplejwt`). A new `apps.chat.infrastructure.jwt_auth_middleware.JWTAuthMiddleware`
validates the same access token, passed as a `?token=` query parameter (browsers
cannot set custom headers on a WebSocket handshake) — the standard workaround for
JWT-over-WebSocket, not a bespoke auth scheme.

API surface: `GET /api/chat/channels/me/`, `POST /api/chat/channels/direct/`,
`POST /api/chat/channels/group/`, `POST /api/chat/channels/{id}/members/`,
`GET`/`POST /api/chat/channels/{id}/messages/`, `POST /api/chat/messages/{id}/flag/`
(supervisor-only). WebSocket: `wss://.../ws/chat/{channel_id}/?token=...`.

## Consequences

- A minor cannot be privately messaged by, or privately message, anyone except a
  supervisor — enforced at the service layer, so it cannot be bypassed by using
  the WebSocket instead of the REST API or vice versa.
- Messages are a permanent record; nothing sent in chat can be silently erased,
  which matters both for safeguarding review and for general moderation.
- `manage.py runserver` gains WebSocket support automatically in development
  because `daphne` is installed and listed before `django.contrib.staticfiles` in
  `INSTALLED_APPS` (Channels' documented mechanism) — no separate dev server
  process needed.
- **Production deployment note**: `gunicorn` (already used for other Django
  services in this repo) only serves WSGI and cannot handle WebSocket upgrades.
  A production ASGI process (`daphne -b 0.0.0.0 -p 8000 config.asgi:application`,
  or `uvicorn`) is required for `apps.chat` to work outside of local dev. This is
  a deploy/start-command decision, not a code change, and is left to whichever
  platform (Railway, etc.) hosts the backend — see `.env.example` and the
  eventual deployment runbook.

## Future considerations

- No push notification on new message when the recipient isn't connected via
  WebSocket — the `apps.notifications` push/WhatsApp channels (ADR 0013) exist
  but chat doesn't call them yet. Worth adding once real usage shows unread
  messages are actually missed.
- No read receipts / unread-count tracking.
- No rate limiting on message sends (REST throttling exists elsewhere via
  `ScopedRateThrottle`, but the WebSocket path has none) — revisit if spam/abuse
  becomes a real problem rather than a theoretical one.
- No profanity/keyword auto-flagging — moderation today is entirely human
  (supervisor-initiated `flag_message`). An automated first-pass filter would be
  a reasonable future addition given the youth-safety context, but needs a
  product decision on false-positive tolerance before building it.
