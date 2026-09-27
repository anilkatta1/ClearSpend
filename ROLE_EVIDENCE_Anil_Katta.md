# Role evidence — Anil Katta

**Role:** Engineer — architecture, implementation, reliability, tests, deployment, and telemetry

**Evidence date:** 27 September 2026  
**Primary repository identity:** `anilkatta1` / `akatta`

## Accountable engineering delivery

| Area | Delivered contribution | Inspectable evidence |
|---|---|---|
| Architecture and technical direction | Defined the bounded reimbursement-review architecture: Next.js frontend, FastAPI modular-monolith API, PostgreSQL consistency boundary, Procrastinate jobs, bounded LangGraph assessment, private S3-compatible receipt storage, and isolated malware scanning. Recorded trade-offs against Redis/Kafka, autonomous agents, model-only policy enforcement, and broad spend management. | [`docs/architecture/as-built-architecture.md`](docs/architecture/as-built-architecture.md), [`docs/adr/`](docs/adr/), [`TECHNICAL_ARCHITECTURE_IMPLEMENTATION_PLAN.md`](TECHNICAL_ARCHITECTURE_IMPLEMENTATION_PLAN.md); commits `7677108`, `e17f0da`, `e4b9e12` |
| Core implementation | Implemented the employee submission, durable assessment, human review, request-information/resubmission, approval/rejection, accounting coding, CSV export, and auditor trace flow. | [`services/backend/app/`](services/backend/app/), [`apps/web/app/page.tsx`](apps/web/app/page.tsx), [`scripts/smoke.py`](scripts/smoke.py); commits `e17f0da`, `87444ec`, `5b396f1` |
| Deterministic and bounded-AI controls | Kept objective policy and merchant/date/amount receipt checks deterministic, made rejection precedence fail closed, and limited LangGraph/model assistance to advisory semantic assessment with no tools or final financial authority. | [`services/backend/app/rules.py`](services/backend/app/rules.py), [`services/backend/app/graph.py`](services/backend/app/graph.py), [`services/backend/app/ai.py`](services/backend/app/ai.py), backend tests; commits `e17f0da`, `1d6c975` |
| Multi-receipt workflow and correction loop | Changed the approval boundary from one receipt per ticket to one same-category report containing up to 20 receipt lines. Added server-derived aggregates, per-line matching, append-only missing-receipt continuation, immutable replacements, and one report-level human decision. | [`apps/web/app/page.tsx`](apps/web/app/page.tsx), [`services/backend/app/main.py`](services/backend/app/main.py), [`services/backend/app/db.py`](services/backend/app/db.py); commits `7968bb1`, `e469a96`, `7d1b046` |
| Receipt usability | Added local multi-file staging, editable extracted merchant/date/amount fields, an icon-only authorized preview dialog, contextual action-required handling, and reusable synthetic demo receipts. | [`apps/web/app/page.tsx`](apps/web/app/page.tsx), [`demo/receipts/`](demo/receipts/), [`README.md`](README.md); commits `4a9e392`, `2f847ab`, `0b63ae9` |
| Security and data handling | Implemented format and deep-document validation, encrypted quarantine/clean object storage, fail-closed ClamAV scanning, prompt-injection indicators, tenant-scoped access, receipt version history, authorized decryption for preview, and hash-linked audit events. | [`docs/security/threat-model.md`](docs/security/threat-model.md), [`services/backend/app/receipt_security.py`](services/backend/app/receipt_security.py), [`services/backend/app/receipt_storage.py`](services/backend/app/receipt_storage.py), [`services/backend/app/audit.py`](services/backend/app/audit.py); commit `3185a52` |
| Reliability and risk-based testing | Added state/rule boundary tests, database-backed outbox recovery, idempotency and tenant-isolation checks, export failure/retry coverage, audit tamper checks, security tests, frontend tests, and a complete synthetic smoke journey. | [`docs/engineering/verification.md`](docs/engineering/verification.md), [`services/backend/tests/`](services/backend/tests/), [`apps/web/lib/api.test.ts`](apps/web/lib/api.test.ts), [`scripts/smoke.py`](scripts/smoke.py); commits `5b396f1`, `1d6c975` |
| Reproducibility and operations | Supplied lockfiles, Docker Compose, migrations/seed data, one-command demo/test targets, CI, health checks, local runbook, optional pgAdmin, and a reproducible S3-compatible container pinned by immutable digest after the former registry image became unavailable. | [`compose.yaml`](compose.yaml), [`.github/workflows/ci.yml`](.github/workflows/ci.yml), [`Makefile`](Makefile), [`docs/operations/local-runbook.md`](docs/operations/local-runbook.md); commits `a1ed580`, `78fe7ef` |
| Product and evidence collaboration | Converted product assessment into receipt-first and post-decision handoff changes; maintained the decision log, architecture boundaries, submission audit, AI-spend reconstruction, and honest real-user evidence traceability without converting estimates into billed spend or discovery into measured outcomes. | [`docs/product/ramp-release-response.md`](docs/product/ramp-release-response.md), [`docs/decision-log.md`](docs/decision-log.md), [`docs/evidence/anil-ai-spend-log.md`](docs/evidence/anil-ai-spend-log.md), [`docs/evidence/real-user-evidence-report.md`](docs/evidence/real-user-evidence-report.md); commits `87444ec`, `d159f75`, `e251f6e` |

## Major engineering decisions owned or implemented

1. Use deterministic policy evaluation before optional AI, and preserve human authority for every financial decision.
2. Use PostgreSQL plus Procrastinate for durable work rather than introducing Redis/Celery or Kafka into the MVP.
3. Use a bounded LangGraph workflow rather than a free-running multi-agent system.
4. Treat receipts as untrusted evidence: encrypted quarantine → malware/format/injection checks → encrypted clean storage → authorized preview.
5. Preserve append and replacement history instead of overwriting receipt evidence.
6. End the MVP at a recorded accountant-ready CSV; do not claim payment, ERP acceptance, or employee settlement.
7. Keep the product runnable offline with a deterministic fake AI provider; the optional live-model adapter is not required for verification.

The decision rationale and rejected alternatives are recorded in [`docs/decision-log.md`](docs/decision-log.md) and the ADRs.

## Verification owned

- Backend Ruff, strict mypy, Pytest/Hypothesis, migrations, and PostgreSQL integration coverage.
- Frontend ESLint, TypeScript, Vitest, and production build.
- Compose configuration, container builds, health checks, and synthetic end-to-end smoke journey.
- GitHub Actions backend, frontend, and container jobs. Run `#31` verified the object-storage registry repair; run `#32` verified the current evidence documentation commit.
- Receipt, malware, tenant-isolation, information-request, export, and audit-chain risk paths documented in [`docs/engineering/verification.md`](docs/engineering/verification.md).

## Cross-functional contribution

- Translated the product assessment into shipped receipt-first, correction-loop, preview, accounting-handoff, and risk-test changes.
- Supported PM evidence integrity by distinguishing implemented facts, qualitative findings, reconstructed estimates, and unvalidated commercial claims.
- Added synthetic receipts, screenshots, demo/run documentation, and pgAdmin access to make the product easier for PM, Sales, reviewers, and assessors to evaluate.
- Kept broader procurement, cards, payment rails, and autonomous finance actions outside the committed MVP.

## Community-post evidence

The available community evidence and missing permalinks are recorded in [`docs/evidence/community-evidence-anil.md`](docs/evidence/community-evidence-anil.md). The user supplied one recent anonymized thread excerpt, but direct post/reply URLs were not available in the repository when this role record was prepared. URLs or permitted screenshots must be added from the actual community platform; they are not fabricated here.

## AI collaboration and spend

Codex assisted with repository inspection, implementation, debugging, documentation, and verification. Anil remained accountable for reviewing and accepting changes. Exact local project token counters and the transparent cost reconstruction are in [`docs/evidence/anil-ai-spend-log.md`](docs/evidence/anil-ai-spend-log.md); the value is an estimate rather than a billing-owner-confirmed invoice. Shared use, verification, rejected suggestions, and runtime boundaries are in [`docs/ai-collaboration-disclosure.md`](docs/ai-collaboration-disclosure.md).

## Known gaps not claimed as complete

- Community post and constructive-reply permalinks are still required in the role record.
- Direct observed product sessions, quantified time saved, and willingness-to-pay evidence remain incomplete.
- Production OIDC/MFA, managed KMS, restore rehearsal, and external accounting acceptance are not part of the demonstrated local MVP.
- Niraj requires a separate Sales role-evidence file for Niraj's own archive; this file does not claim Sales contributions on his behalf.

