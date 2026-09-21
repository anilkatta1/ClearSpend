# MVP threat model

| Threat | Current control | Production gate |
|---|---|---|
| Cross-tenant object access | Organization comes from the principal; scoped queries; employee ownership filter; opaque object keys; objects are never addressed directly by clients; second synthetic tenant smoke denial | Add PostgreSQL RLS and broader automated tenant-isolation integration tests |
| Role escalation / self approval | Central FastAPI role dependencies; no role accepted in request bodies; employee/reviewer/auditor views are scoped; submitter cannot review the same expense | Replace demo header with OIDC, hardened sessions, MFA, and authorization audit |
| Malicious upload | Size and magic-byte allowlist before storage; encrypted quarantine; ClamAV in a separate service before any image/PDF parser; fail-closed scanner errors; only clean objects are promoted/downloadable | Monitor signature freshness, use managed isolated scanning, add retention and incident workflow |
| Parser abuse / decompression bomb | Exact MIME/format checks, Pillow verification, 25 MP image cap, single-frame image rule, 20-page PDF cap, encrypted/executable/embedded PDF rejection; passive initial-page destination arrays remain supported | OS-level resource quotas and adversarial corpus fuzzing |
| Prompt injection | OCR text is flagged before AI; suspicious receipt or claim text adds an `UNKNOWN` guardrail check and prevents model invocation; structured output; allowlisted citations; AI has no tools/write authority | Expand red-team evaluation set and establish provider/model release gate |
| Model outage or invalid output | Typed adapter outcome; fail closed to human review | Alert on fallback rate and queue/service SLOs |
| Duplicate or stale decisions | Idempotency keys, row locks, optimistic row version, state machine | Load/concurrency tests against managed PostgreSQL |
| Audit modification | Append-only application path and per-tenant hash chain verification | Restricted DB role, backups, retention policy, external integrity anchor |
| Receipt or personal-data leakage | AES-256-GCM object encryption with object-key-bound AAD; authorized server-side decryption; hashes/IDs rather than receipt text in audit/log data; model storage disabled | Managed KMS/envelope encryption, key rotation, DLP/log review, retention/deletion controls, vendor DPA |
| Dependency compromise | Lockfiles, pinned major ranges, pnpm build-script allowlist, CI verification | Automated SCA/SBOM and signed deployment artifacts |

This model covers the bounded reimbursement MVP. It is not an authorization to process production financial or personal data.
