# ClearSpend

ClearSpend is a bounded, human-in-the-loop finance-operations assistant for reimbursement review. An employee uploads a receipt first, verifies extracted fields, and submits a claim. Deterministic policy and receipt checks run before an optional AI assessment; a finance reviewer always owns the final decision. Approved claims move to a human-confirmed accounting-code step and an accountant-ready CSV—never money movement.

## Stack

- Next.js + TypeScript frontend
- FastAPI + SQLAlchemy backend
- PostgreSQL for domain state and Procrastinate jobs
- Procrastinate worker containing a bounded LangGraph workflow
- Fake AI provider by default; optional OpenAI adapter

## Run

```bash
cp .env.example .env
make demo
```

Open <http://localhost:3000>. Demo identities are selected in the UI. API docs are at <http://localhost:8000/docs>.

The release flow is:

1. Employee uploads a JPEG, PNG, or PDF receipt and verifies the extracted merchant, date, and INR amount.
2. The durable worker evaluates deterministic policy and receipt matching, then uses bounded LangGraph assistance only for ambiguity.
3. A reviewer sees evidence and pinned policy citations, then approves, rejects, or requests named information.
4. Approval enters `READY_TO_EXPORT`; a reviewer confirms account coding and downloads the recorded CSV export.

## Verify

```bash
make test
make verify
python scripts/smoke.py
```

See `TECHNICAL_ARCHITECTURE_IMPLEMENTATION_PLAN.md`, `CONTEXT.md`, `docs/adr/`, and `docs/operations/local-runbook.md` for architecture and operations. The product-team response and deferred boundaries are in `docs/product/ramp-release-response.md`. Grading evidence is indexed in `docs/evidence/rubric-matrix.csv`; the decision and AI records are in `docs/decision-log.md` and `docs/ai-collaboration-disclosure.md`.
