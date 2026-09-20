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
- Authenticated encryption round trip, cross-key/object-key denial, and ciphertext tamper rejection
- Shallow signature validation separated from post-malware deep document parsing
- Live ClamAV EICAR detection using a synthetic PDF and quarantined-content download denial
- Receipt replacement creates an immutable second revision and exactly one current association
- Deterministic prohibition short-circuiting AI
- Hash-linked audit integrity and tamper detection
- Concurrent authorized receipt reads preserve the per-tenant audit chain
- Frontend money formatting contract

The live smoke also covers cross-tenant receipt/expense denial, request-information/resubmission/reassessment, reviewer-only decisions, CSV export, and product metrics. Before a customer-data pilot, add OIDC/session tests, PostgreSQL RLS tests, scanner-outage fault injection, migration rollback, key rotation, and backup/object-store restore exercises.
