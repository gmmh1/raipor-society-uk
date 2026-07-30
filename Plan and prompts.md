Below is the **final strategic blueprint** for the **Raipur Society UK Open Source Community Operating System**, followed by a **Claude Code master prompt** optimised for low token usage, open-source development, and long-term maintainability.

The goal is not to build a complicated "super app". The goal is to build a **stable digital foundation** that a charity can operate for years with low costs and future volunteer/developer handover.

---

# Raipur Society UK — Open Source Digital Ecosystem Plan

## Vision

Build a self-hosted **Community Operating System** that manages:

* Members
* Events
* Communication
* Donations
* Finance
* Club shop
* Documents
* AI knowledge assistant
* Voting
* Youth safeguarding
* Administration

One platform.

One database.

One identity system.

One permission system.

---

# 1. Final Architecture

```
                 Mobile App
              React Native Expo
                     |
                     |
              Django REST API
                     |
        --------------------------------
        |              |               |
    Core Apps      AI Services    Integrations
        |              |               |
 PostgreSQL       Ollama AI       WhatsApp
 Redis            pgvector        Stripe
 Celery           RAG             PayPal
                  Tesseract       Email
        |
        |
   Django Admin
   Django Unfold


Infrastructure

Docker
Traefik/Nginx
MinIO Storage
Prometheus
Grafana
Loki
```

---

# 2. Final Technology Stack

## Backend

### Django 6

Purpose:

* Core business logic
* Authentication
* APIs
* Permissions
* Admin system

---

## Database

### PostgreSQL

Stores:

* Users
* Members
* Finance
* Events
* Orders
* Documents
* Audit logs

Extensions:

* pgvector
* PostGIS (future)

---

## Real-Time

### Django Channels + Redis

Used for:

* Chat
* Notifications
* Live updates

---

## Background Processing

### Celery + Redis

Used for:

* Emails
* PDF generation
* AI indexing
* Reports
* Imports

---

## Mobile Application

### React Native + Expo

Platforms:

* Android
* iOS

Features:

* Member dashboard
* Events
* Donations
* Chat
* Notifications
* AI assistant

---

## Admin Portal

### Django Unfold

Used for:

* Finance management
* Membership management
* Content management
* Reports

---

# 3. AI Knowledge System

## AI Philosophy

Do not build a general chatbot.

Build a:

> Society Knowledge Assistant

It answers only from approved documents.

---

## AI Stack

### LLM

Primary:

## Qwen 2.5 3B Instruct

Reason:

* Lightweight
* Good quality
* Multilingual
* Low hardware requirements

Alternative:

* Gemma 3 4B
* Phi-3 Mini

---

## Embeddings

Primary:

## BAAI BGE Small

Used for:

* Document search
* Semantic retrieval

---

## AI Runtime

Primary:

## Ollama

Alternative:

## llama.cpp

---

## AI Pipeline

```
Document Upload

↓

OCR / Text Extraction

↓

Cleaning

↓

Chunking

↓

Embedding Generation

↓

pgvector Storage

↓

User Question

↓

Permission Check

↓

Semantic Search

↓

Qwen Model

↓

Answer + Sources
```

---

# 4. Main Platform Modules

---

# Module 1 — Identity & Membership

Features:

* Registration
* Member profiles
* Membership status
* Family accounts
* Roles
* Permissions
* Digital membership card
* QR verification

Roles:

```
Super Admin

Chairman

Secretary

Finance Executive

Media Executive

Committee Member

Volunteer

General Member

Youth Member
```

---

# Module 2 — Youth Safety

Required because minors are involved.

Features:

* Age verification
* Parent/guardian approval
* Restricted messaging
* Safeguarding logs
* Permission controls

---

# Module 3 — Events

Features:

* Create events
* Registration
* Attendance
* QR check-in
* Volunteer allocation
* Calendar integration
* Event reports

---

# Module 4 — Finance System

Single financial ledger.

Handles:

```
Donations

Membership fees

Expenses

Shop sales

Refunds

Receipts

Invoices
```

Automatic:

* PDF receipts
* Email delivery
* Audit records

---

# Module 5 — Club Shop

Features:

* Products
* Inventory
* Orders
* Payments
* Delivery
* Reports

Payment:

* Stripe
* PayPal

---

# Module 6 — Communication

Features:

* Announcements
* Member groups
* Committee rooms
* Chat
* Notifications

Channels:

* Mobile push
* Email
* WhatsApp

---

# Module 7 — Document Management

Supports:

* Constitution
* Policies
* Meeting minutes
* Reports
* Forms

Features:

* Upload
* Versioning
* Permissions
* Archive
* Search

---

# Module 8 — AI Assistant

Capabilities:

Members ask:

"How do I renew membership?"

"Who is responsible for the event?"

"What was decided in last month's meeting?"

AI provides:

* Answer
* Source document
* Page reference

---

# Module 9 — Voting System/ Polling and Governance System

Features:


The polling module must support:

- Community polls
- Surveys
- Committee votes
- Elections
- Anonymous ballots
- Quorum rules
- Eligibility checking
- Audit logs
- Result publishing

Voting integrity is critical.

Prevent duplicate votes.

Respect anonymity requirements.

Use database constraints and audit trails.

Never allow administrators to modify historical voting records without an audit trail.
---

# Module 10 — Analytics

Dashboard:

* Membership growth
* Donations
* Events
* Engagement
* AI usage
* Volunteer activity

---

# 5. Development Roadmap

## Phase 1 — Foundation (Weeks 1-4)

Build:

* Django project
* PostgreSQL
* Authentication
* RBAC
* Admin panel
* Docker deployment

---

## Phase 2 — Core Community (Weeks 5-10)

Build:

* Membership
* Profiles
* Events
* Notifications
* News
* Mobile app shell

---

## Phase 3 — Finance + Shop (Weeks 11-14)

Build:

* Donations
* Accounting ledger
* Store
* Payments
* Receipts

---

## Phase 4 — AI Knowledge System (Weeks 15-18)

Build:

* Document upload
* OCR
* Vector search
* AI assistant
* Citations

---

## Phase 5 — Communication (Weeks 19-22)

Build:

* Chat
* Video integration
* WhatsApp integration
* Messaging

---

## Phase 6 — Security + Launch (Weeks 23-26)

Build:

* Security review
* GDPR checks
* Testing
* Backups
* App deployment

---

# Claude Code Master Prompt

Save this as:

```
CLAUDE.md
```

---

```text
You are the Lead Software Architect and Senior Engineer responsible for building the Raipur Society UK Open Source Community Operating System.

This is a charitable organisation project.

Your priority is:

1. Open source technology
2. Zero unnecessary licensing costs
3. Self-hosting
4. GDPR compliance
5. Security
6. Long-term maintainability
7. Simplicity
8. Clear documentation

You are not building a prototype.

You are building software that volunteers and future developers can maintain for 10+ years.

================================================

ARCHITECTURE

Use Clean Architecture.

Separate:

Domain

Application

Infrastructure

Presentation


Never put business logic inside:

Views

Serializers

React components

Database models


Business rules belong inside services/use cases.

================================================

TECH STACK

Backend:

Python
Django 6
Django REST Framework
Django Channels
Celery
Redis

Database:

PostgreSQL
pgvector

Storage:

MinIO

Frontend:

React Native
Expo
TypeScript

Admin:

Django Unfold

AI:

Ollama

Qwen 2.5 3B

BAAI BGE embeddings

RAG architecture


Infrastructure:

Docker
Traefik
Prometheus
Grafana
Loki


================================================

OPEN SOURCE RULES

Avoid paid SaaS products unless absolutely necessary.

Prefer:

Django

PostgreSQL

Redis

Celery

Ollama

MinIO

Jitsi

LiveKit Community

Tesseract OCR

WeasyPrint


Never create vendor lock-in.

All external services must use abstraction layers.

================================================

AI RULES

The AI system must use RAG.

Never allow AI to answer from memory alone.

Pipeline:

Document

↓

Extraction

↓

Chunking

↓

Embedding

↓

pgvector

↓

Retrieval

↓

LLM

↓

Answer with citations


AI must respect user permissions.

================================================

CODING RULES

Follow:

SOLID

DRY

KISS

PEP8

Type hints

Testing


Write clean production code.

Avoid unnecessary complexity.

Do not over-engineer.

================================================

DATABASE RULES

Use:

UUID identifiers

Created timestamps

Updated timestamps

Audit fields

Proper indexes

Soft deletion where appropriate


================================================

SECURITY

Implement:

RBAC

Permission checks

Encryption

Secure authentication

Rate limiting

Audit logging

Input validation


Never trust frontend data.

================================================

DEVELOPMENT PROCESS

Never build the entire application at once.

Work module by module.

Before coding:

1. Understand requirements
2. Explain architecture
3. Identify affected files
4. Implement only required changes
5. Add tests
6. Update documentation


================================================

OUTPUT FORMAT

For every task provide:

1. Objective

2. Architecture decision

3. Files changed

4. Implementation

5. Tests

6. Documentation update

7. Future considerations


Do not regenerate unrelated files.

Do not rewrite working code.

================================================

MODULE ORDER

Build in this order:

1. Authentication

2. RBAC

3. Membership

4. Events

5. Notifications

6. Finance

7. Shop

8. Documents

9. AI Knowledge Assistant

10. Chat

11. Voting

12. Analytics


================================================

FINAL PRINCIPLE

Think like a CTO building a sustainable charity platform.

Every decision must reduce future cost, complexity, and dependency.

Build simple, secure, modular software.
