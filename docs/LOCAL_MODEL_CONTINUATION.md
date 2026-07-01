# Local Model Continuation Guide (Qwen2.5-Coder)

This guide lets a local model continue the same project with the same rules and execution style.

## 1. What is parity and what is not

- You can get architecture and workflow parity by reusing the same repo instructions and handoff context.
- You cannot get 1:1 tool parity with hosted agent-only tools unless your local IDE/agent provides equivalents.
- In practice, parity is achieved by combining:
  - shared instruction files
  - consistent task format
  - generated handoff context file

## 2. Source of truth files to always load first

Load these files into your local model context at the start of each session:

1. `CLAUDE.md`
2. `docs/EXECUTABLE_PLAN.md`
3. `docs/DEPLOYMENT_WEB_VERCEL_CLOUDFLARE.md`
4. `docs/QWEN_LOCAL_SYSTEM_PROMPT.md`
5. `docs/LOCAL_MODEL_SESSION_CONTEXT.md` (generated each session)

## 3. Generate handoff context before switching models

Run this command from repo root (works on Windows without make):

```powershell
pwsh -File scripts/export-local-handoff.ps1
```

This generates `docs/LOCAL_MODEL_SESSION_CONTEXT.md` with:

- git branch and latest commit
- current working tree status
- staged and unstaged changes
- recent commit history

For one command that generates both the handoff context and a ready-to-copy starter prompt, run:

```powershell
pwsh -File scripts/local-qwen-session.ps1
```

This also creates `docs/LOCAL_MODEL_START_PROMPT.md`.

If you have `make` installed, equivalent shortcuts are available:

```text
make local-handoff
make local-qwen
```

## 4. Start local model with same project rules

### Ollama example

```powershell
ollama pull qwen2.5-coder:7b
```

Use your local editor assistant to set:

- system prompt: contents of `docs/QWEN_LOCAL_SYSTEM_PROMPT.md`
- session context: contents of `docs/LOCAL_MODEL_SESSION_CONTEXT.md`

If your local tool supports repo indexing/RAG, include the `docs/` folder and `CLAUDE.md` as high-priority retrieval sources.

## 5. Recommended task prompt template

Use this message for each task:

```text
Continue implementation in this repository using existing architecture constraints.
Read and follow: CLAUDE.md, docs/EXECUTABLE_PLAN.md, docs/QWEN_LOCAL_SYSTEM_PROMPT.md, docs/LOCAL_MODEL_SESSION_CONTEXT.md.
Implement the smallest safe patch, add/update tests, and update docs for operational impact.
Output in this order:
1) Objective
2) Architecture decision
3) Files changed
4) Implementation
5) Tests
6) Documentation update
7) Future considerations
```

## 6. Module safety gate

Before implementing features, confirm target module matches the ordered roadmap:

- Authentication -> RBAC -> Membership -> Events -> Notifications -> Finance -> Shop -> Documents -> AI -> Chat -> Voting -> Analytics

If asked to skip ahead, record justification in docs and keep interfaces stable.

## 7. Local-run quick commands

```powershell
# backend stack
pwsh -File scripts/bootstrap.ps1

# web
cd web
npm install
npm run dev

# mobile
cd mobile
npm install
npm run typecheck
```

## 8. Definition of done

A task is done only if all are true:

- code compiles/lints/tests for impacted area
- docs updated where behavior or operations changed
- no unrelated files changed
- git status is intentional and reviewable
