# AI collaboration disclosure

## Use in this implementation

OpenAI Codex assisted with repository inspection, architecture synthesis, code generation, documentation, and test execution. The accountable engineer remains responsible for reviewing, understanding, and accepting every change.

Material AI-assisted areas include:

- FastAPI, SQLAlchemy, Alembic, and Procrastinate scaffolding;
- deterministic policy domain and LangGraph workflow implementation;
- Next.js demonstration interface;
- Docker Compose, CI, tests, ADRs, threat model, and runbook;
- diagnosis of dependency, lint, container import-path, and worker enqueue issues.

## Verification and rejected suggestions

Generated work was checked using strict mypy, Ruff, Pytest/Hypothesis, ESLint, TypeScript, Vitest, a Next.js production build, container image builds, health checks, and a live synthetic end-to-end test. Corrections made during verification included replacing unsupported Procrastinate defer arguments, removing nested event-loop execution, pinning an ESLint-compatible major version, carrying pnpm's build allowlist into Docker, setting the backend container import path, and adding outbox recovery.

The design rejects autonomous AI decisions, AI write tools, model-only policy enforcement, Redis/Kafka for the MVP, and production claims based on synthetic evidence.

## Spend

- Product runtime AI spend during the verified demo: **USD 0.00** (`AI_PROVIDER=fake`).
- Codex development spend: **not exposed in this environment; record the billed amount from the account usage report before submission**.
- Local compute and engineering time are not included in the USD figure and must not be represented as zero total cost.

Before final submission, add the actual model/tool identifiers, available token counts, and billed AI amount from the team account.

