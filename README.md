# ClearSpend

ClearSpend is a bounded, human-in-the-loop finance-operations assistant for reimbursement review. Deterministic policy checks run before an optional AI assessment; a finance reviewer always owns the final decision.

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

## Verify

```bash
make test
make verify
```

See `TECHNICAL_ARCHITECTURE_IMPLEMENTATION_PLAN.md`, `CONTEXT.md`, `docs/adr/`, and `docs/operations/local-runbook.md` for architecture and operations. Grading evidence is indexed in `docs/evidence/rubric-matrix.csv`; the decision and AI records are in `docs/decision-log.md` and `docs/ai-collaboration-disclosure.md`.
