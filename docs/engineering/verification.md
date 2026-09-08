# Engineering verification

Run the local quality gate:

```bash
make verify
```

The gate checks Ruff, strict mypy, backend tests, ESLint, TypeScript, frontend tests, and Docker Compose validity. CI repeats these checks from lockfiles and builds all container images.

## Risk-based test inventory

- State-machine transitions and invalid transition rejection
- Money/currency and deterministic rule boundary behavior
- Fail-closed aggregation for unknown and technical outcomes
- Prompt-injection-like semantic input
- Deterministic prohibition short-circuiting AI
- Hash-linked audit integrity and tamper detection
- Frontend money formatting contract

Before a customer pilot, add PostgreSQL-backed API integration tests for tenant isolation, concurrent decisions, outbox recovery, worker retry, migration rollback, and backup restore.

