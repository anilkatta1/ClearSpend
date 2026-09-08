# Decision log

| Date | Decision | Evidence/rationale | Rejected alternative | Verification |
|---|---|---|---|---|
| 2026-09-07 | Bound the product to reimbursement review | Deadline and trust rubric reward a complete risky flow | General finance copilot | Seeded submit → assess → decide → audit smoke path |
| 2026-09-07 | Next.js frontend and FastAPI backend | Team preference, typed browser UI, Python AI ecosystem | Node.js domain API | Independent production builds and API contract |
| 2026-09-07 | PostgreSQL plus Procrastinate | Durable jobs without another operational service | Redis/Celery or Kafka | Schema boot, worker processing, zero pending outbox |
| 2026-09-08 | Deterministic rules precede AI | Thresholds and prohibitions require reproducible outcomes | Model-only policy adjudication | Precedence, boundary, and short-circuit tests |
| 2026-09-08 | LangGraph is bounded orchestration | Branching and fallback are useful; autonomous agency is not | Multi-agent swarm | Injection-like case routes to review; AI has no tools |
| 2026-09-08 | Human reviewer owns final state | Financial authority and override accountability | Automatic reimbursement approval | RBAC decision endpoint and audit event |
| 2026-09-08 | Transactional outbox plus queue locks | API-to-worker delivery must survive enqueue failure | Best-effort enqueue only | Live outbox relayed and pending count returned to zero |
| 2026-09-08 | Fake AI by default, configurable OpenAI adapter | Reproducible demo without external spend | Live model required for every run | Unit suite is offline; live adapter uses structured output and no tools |

This log records architecture decisions. Interview-driven product decisions must be added as `hypothesis → evidence → decision`, without private participant data.

