# MVP threat model

| Threat | Current control | Production gate |
|---|---|---|
| Cross-tenant object access | Organization comes from the principal; scoped queries; second synthetic tenant | Add PostgreSQL RLS and automated tenant-isolation integration tests |
| Role escalation | Central FastAPI role dependencies; no role accepted in request bodies | Replace demo header with OIDC, hardened sessions, MFA, and authorization audit |
| Prompt injection | Input treated as untrusted data; structured output; allowlisted citation IDs; AI has no write tools | Red-team evaluation set and provider/model release gate |
| Model outage or invalid output | Typed adapter outcome; fail closed to human review | Alert on fallback rate and queue/service SLOs |
| Duplicate or stale decisions | Idempotency keys, row locks, optimistic row version, state machine | Load/concurrency tests against managed PostgreSQL |
| Audit modification | Append-only application path and per-tenant hash chain verification | Restricted DB role, backups, retention policy, external integrity anchor |
| Secret or personal-data leakage | Synthetic seed data; no receipt binaries; model storage disabled | Secret manager, DLP/log review, retention/deletion controls, vendor DPA |
| Dependency compromise | Lockfiles, pinned major ranges, pnpm build-script allowlist, CI verification | Automated SCA/SBOM and signed deployment artifacts |

This model covers the bounded reimbursement MVP. It is not an authorization to process production financial or personal data.

