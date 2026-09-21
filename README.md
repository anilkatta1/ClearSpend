# ClearSpend

ClearSpend is a bounded, human-in-the-loop finance-operations assistant for reimbursement review. An employee can upload up to 20 same-category receipts, verify each line, and submit them as one expense report and one approval ticket. Deterministic aggregate-policy and per-receipt checks run before optional AI assistance; a finance reviewer always owns the final decision. Approved reports move to a human-confirmed accounting-code step and a line-level accountant-ready CSV—never money movement.

## Stack

- Next.js + TypeScript frontend
- FastAPI + SQLAlchemy backend
- PostgreSQL for domain state and Procrastinate jobs
- MinIO private object storage with application-side AES-256-GCM receipt encryption
- ClamAV in an isolated service for fail-closed malware scanning
- Procrastinate worker containing a bounded LangGraph workflow
- Fake AI provider by default; optional OpenAI adapter

## Run

```bash
cp .env.example .env
make demo
```

Open <http://localhost:3000>. Demo identities are selected in the UI. API docs are at <http://localhost:8000/docs>.

The release flow is:

1. Employee selects one or many JPEG, PNG, or PDF receipts for the same category. ClearSpend encrypts each into quarantine, malware-scans before parsing, validates structure, and promotes only clean objects for preview and extraction.
2. The employee verifies merchant, date, and amount per line. The server derives the report total, oldest incurred date, and bundle hash; clients cannot assert a different aggregate.
3. The durable worker evaluates aggregate policy plus deterministic merchant/date/amount matching for every receipt, then uses bounded LangGraph assistance only for ambiguity.
4. A reviewer sees all receipt lines and pinned policy citations, then makes one decision for the report. A request for a missed receipt appends only the new evidence; explicit replacement creates a new complete bundle revision. Prior evidence remains visible to auditors.
5. Approval enters `READY_TO_EXPORT`; a reviewer confirms account coding and downloads a recorded CSV containing one accounting line per current receipt.

## Verify

```bash
make test
make verify
python scripts/smoke.py
```

See `TECHNICAL_ARCHITECTURE_IMPLEMENTATION_PLAN.md`, `CONTEXT.md`, `docs/adr/`, and `docs/operations/local-runbook.md` for architecture and operations. The product-team response and deferred boundaries are in `docs/product/ramp-release-response.md`. Grading evidence is indexed in `docs/evidence/rubric-matrix.csv`; the decision and AI records are in `docs/decision-log.md` and `docs/ai-collaboration-disclosure.md`.
