# ADR 0018: Analytics — Live-Aggregated Governance and Operations Dashboards

## Status

Accepted

## Context

Module 12 (Analytics) is the last module in `CLAUDE.md`'s build order: "Analytics
dashboards for governance and operations." Every other module (Membership,
Events, Finance, Shop, Documents, Chat, Voting) now has real data to report on.

## Decision

New `apps.analytics` module with **no persisted models** — every report is
computed live from existing tables via straightforward ORM aggregation
(`Count`, `Sum`), not a separate data warehouse or materialized summary table.
`apps.analytics.application.reports` exposes one function per domain
(`membership_report`, `events_report`, `finance_report`, `shop_report`,
`documents_report`, `assistant_report`, `chat_report`, `voting_report`) plus
`overview_report()`, which assembles all of them into a single dict — this is
the one place in the codebase that intentionally imports across nearly every
other module, and it's kept isolated here rather than scattered.

Each report function lazy-imports its target app's models inside the function
body (not at module level) — avoiding a large import-time fan-out across every
other app just to define `apps.analytics`, and keeping each report trivially
readable in isolation.

API: `GET /api/analytics/overview/`, staff-only (`admin`/`treasurer` — the same
roles that already see `apps.finance`'s reconciliation summary and
`apps.membership`'s admin list, since this is operational/governance data, not
member-facing).

`finance_report` reuses `apps.finance.application.payment_service.reconciliation_summary`
directly rather than re-deriving the variance calculation — the same
single-source-of-truth instinct as every other cross-module call in this
codebase (ADR 0012, 0014, 0015).

## Consequences

- No risk of a reporting table drifting out of sync with the source data — there
  is no copy to drift, every number is computed on request.
- No caching, so `overview/` does a nontrivial number of queries per request. At
  today's data volume (a single-charity ops team polling a dashboard
  occasionally) this is a non-issue in practice.
- Adding a report for a new module (e.g. once Chat or Voting data grows) means
  adding one function to `reports.py`, not designing a schema migration.

## Future considerations

- If dashboard polling frequency or data volume ever makes live aggregation
  slow, the natural next step is either (a) caching `overview_report()`'s
  result for a short TTL (Redis is already in the stack), or (b) a genuine
  materialized reporting table refreshed by a Celery beat task — not a
  redesign of this module, just adding a cache/materialization layer in front
  of the same report functions.
- No time-range filtering (e.g. "this quarter" vs. all-time) beyond the
  hardcoded 7/30-day windows already in `assistant_report`/`finance_report`.
  Add query-parameter-driven date ranges if governance reporting needs them.
- No per-report endpoints (`/api/analytics/finance/`, etc.) — only the combined
  `overview/`. Splitting them out is straightforward if a future frontend wants
  to fetch dashboard widgets independently/incrementally rather than all at
  once.
