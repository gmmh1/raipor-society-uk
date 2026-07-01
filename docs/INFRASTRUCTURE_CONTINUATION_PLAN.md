# Infrastructure Continuation Plan for Social Organizations

This document extends the original Raipor Society UK blueprint into a complete full-stack and operational model covering web, mobile, backend, deployment, and compliance.

## 1. Core Systems and Architectural Blueprint

### A. Core infrastructure layers

1. Presentation layer

- Public website (awareness, events, donation funnels, contact)
- Member web portal (membership, events, documents, voting, AI assistant)
- Admin web portal (membership operations, finance, governance, analytics)
- Mobile apps (React Native/Expo) for member workflows and notifications

2. Application layer

- Django REST API and domain modules
- Channels for real-time communication
- Celery for background jobs and integrations
- Service abstractions for payments, messaging, OCR, and AI retrieval

3. Data and storage layer

- PostgreSQL as system of record
- pgvector for semantic retrieval
- Redis for cache, session, and queue coordination
- MinIO for object/document storage and versioned artifacts

4. Intelligence layer

- OCR extraction
- Chunking and embedding generation
- Permission-aware retrieval
- Qwen answer generation with citations

5. Operations and edge layer

- Dockerized services
- Monitoring with Prometheus, Grafana, Loki
- Vercel frontend hosting
- Cloudflare DNS, SSL, WAF, rate limiting

## 2. Complete system modules and feature coverage

### A. Identity and membership

- Registration and onboarding
- Role-based access model
- Family accounts and youth-member linking
- Digital membership cards and QR verification

### B. Youth safety and safeguarding

- Age verification workflow
- Parent/guardian approvals
- Communication restrictions for minors
- Safeguarding incident logs and review process

### C. Events

- Event creation and publishing
- Registration and attendance tracking
- QR check-in
- Volunteer assignment and event reporting

### D. Finance and donations

- Unified ledger for membership fees, donations, expenses, shop sales, refunds
- Stripe and PayPal adapters behind a payment abstraction layer
- PDF receipts and invoices
- Financial auditability and reconciliation reporting

### E. Club shop

- Product catalog and inventory
- Checkout and payment confirmation
- Order lifecycle and fulfillment records

### F. Communication

- Announcements and group communication
- Chat and notification orchestration
- Email, push, and WhatsApp channels

### G. Document management

- Upload, versioning, archive, and role-restricted access
- Full-text and semantic search capabilities

### H. AI knowledge assistant

- Document-grounded answers only
- Source citation and page references
- Permission checks before retrieval and answer generation

### I. Voting and governance

- Polls, surveys, committee votes, elections
- Anonymous ballots when required
- Eligibility and quorum checks
- Immutable audit logs and tamper-evident records

### J. Analytics

- Membership growth, event engagement, donations, volunteer activity
- Governance and participation reporting

## 3. Full-stack implementation blueprint

### A. Website architecture (Next.js)

- Public routes for outreach and fundraising
- Member routes for authenticated community services
- Admin routes for operational control
- Shared UI components and typed API clients

### B. Mobile architecture (Expo)

- API-driven feature parity for member workflows
- Notification-focused UX for events, announcements, and actions

### C. Backend architecture (Django)

- Clean architecture boundaries per module
- API endpoints as thin adapters to use-case services
- Permission and audit controls at service boundaries

## 4. Deployment and delivery model

### A. GitHub

- Source of truth for code, issues, and pull requests
- Protected main branch with mandatory checks
- CI for backend, mobile, and web

### B. Vercel

- Frontend deployment target for the website
- Preview deployment per PR
- Production deployment on main

### C. Cloudflare

- Domain, DNS, TLS, and edge security
- WAF, bot management, and route-specific rate limiting
- Optional caching rules and page optimization

### D. Backend hosting

- Containerized backend deployment in self-hosted or compatible environment
- CORS and trusted origins configured for frontend domains

## 5. Security and compliance safeguards

### A. Security controls

- RBAC and object-level permission checks
- Input validation and rate limiting
- Encrypted secrets and key-rotation policy
- Immutable audit trails for critical actions

### B. GDPR controls

- Data inventory and lawful basis mapping
- Subject access/export/deletion workflows
- Data retention and deletion schedules
- Processor and sub-processor records

### C. Safeguarding controls

- Restricted interactions for youth members
- Mandatory guardian controls for sensitive actions
- Incident escalation and review logging

## 6. Engineering governance and quality gates

### A. Module delivery sequence

1. Authentication
2. RBAC
3. Membership
4. Events
5. Notifications
6. Finance
7. Shop
8. Documents
9. AI assistant
10. Chat
11. Voting
12. Analytics

### B. Definition of done for each module

- Architecture note (ADR)
- Data model and migrations
- API and use-case implementation
- Tests (unit + integration)
- Documentation and operational runbooks
- Security and permission verification

## 7. Operational readiness checklist

- CI green for backend, web, and mobile
- Monitoring dashboards online
- Backup and restore drill verified
- Incident response runbook tested
- Release rollback path documented
- Domain and TLS validated in Cloudflare
- Production smoke tests on Vercel frontend and backend APIs
