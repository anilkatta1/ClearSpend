# Submission package checklist — Anil Katta

**Audit date:** 27 September 2026  
**Intended archive:** `ClearSpend-Anil_Katta.zip`  
**Packaging command:** `make submission-zip`

## Required contents

| Requirement | Status | Included evidence | Remaining action |
|---|---|---|---|
| Codebase | Pass | `apps/web`, `services/backend`, `compose.yaml`, migrations, scripts | None for bundle presence |
| README | Pass | [`README.md`](../../README.md) describes scope, stack, run, workflow, UI, verification, and packaging | Keep synchronized with final commit |
| Pinned dependencies/lock files | Pass | `services/backend/uv.lock`, `apps/web/pnpm-lock.yaml`; container images are version-pinned and Silo is digest-pinned | None |
| One-command run | Pass | `cp .env.example .env && make demo`; Compose performs migrations, job schema, seed, and startup | First run requires Docker and network access to images/signatures |
| Tests | Pass | Backend unit/property/integration tests, frontend tests, [`scripts/smoke.py`](../../scripts/smoke.py), CI workflow | Archive final CI URL/commit in submission notes |
| Generated evidence/metrics | Pass for implemented MVP | Synthetic receipts, UI screenshots, smoke journey, product metrics endpoint, audit-chain output, [`docs/engineering/verification.md`](../engineering/verification.md) | Customer outcome metrics remain unvalidated and must not be implied |
| Business Model Canvas | Pass as hypothesis artifact | [`docs/product/business-model-canvas.md`](../product/business-model-canvas.md) | Behavioral and paid-commitment tests remain pending |
| Pricing | Pass as hypothesis artifact | [`docs/pricing.md`](../pricing.md), [`docs/sales/pricing-validation.md`](../sales/pricing-validation.md) | Willingness-to-pay result remains missing |
| Research/interview synthesis | Pass for qualitative evidence | Five canonical participant records, synthesis, [real-user evidence report](real-user-evidence-report.md) | Direct timed product observations remain missing |
| Roadmap | Pass | [`docs/product/roadmap.md`](../product/roadmap.md) is sequenced by evidence and risk | Evidence gates are plans until executed |
| Pitch deck | Pass | PDF, PPTX, rendered slides, source/readme, demo narrative | Preserve evidence/hypothesis wording during delivery |
| Decision log | Pass | [`docs/decision-log.md`](../decision-log.md) records decisions, rationale, rejected alternatives, and verification | Add future evidence-driven decisions when they occur |
| AI-collaboration disclosure | Partial | Shared disclosure plus owner logs and billing-attestation register | Billing-owner confirmation and remaining contributor spend are pending |
| Anil role evidence | Pass for contribution trace | [`ROLE_EVIDENCE_Anil_Katta.md`](../../ROLE_EVIDENCE_Anil_Katta.md) maps engineering work to artifacts and commits | Add genuine community post/reply links or permitted screenshots |
| Community links in role evidence | Missing external evidence | [Anil community register](community-evidence-anil.md) records known content and missing fields | Obtain actual community permalinks/captures; do not fabricate or backdate |

## Archive hygiene

| Check | Result |
|---|---|
| Real ZIP integrity | Candidate passed `unzip -tq` |
| Candidate file count | 303 files |
| Candidate uncompressed size | 14,633,993 bytes (about 14.0 MiB), well below 500 MB |
| Real `.env` included | No; `.env` is ignored and untracked |
| `.env.example` included | Yes; synthetic local-demo defaults only, no real account key |
| API keys/private keys included | No matching tracked credential/private-key pattern found |
| Dependency caches/virtual environments | No tracked `node_modules`, `.next`, `.venv`, Python caches, coverage, `dist`, or build directories |
| Private client data | None identified; demo receipts and identities are synthetic |

The candidate inspection proves package shape and size but is not the final upload artifact. After all reviewed changes are committed and CI passes, run `make submission-zip`; the builder refuses a dirty working tree and archives the exact `HEAD` commit.

## Role-file status across the shared bundle

| Learner | Role file | Status |
|---|---|---|
| Anil Katta | [`ROLE_EVIDENCE_Anil_Katta.md`](../../ROLE_EVIDENCE_Anil_Katta.md) | Present; community links pending |
| Diya Mondal | [`ROLE_EVIDENCE_Diya_Mondal.md`](../../ROLE_EVIDENCE_Diya_Mondal.md) | Present; community links pending per file |
| Prashant Chouksey | [`ROLE_EVIDENCE_Prashant_Chouksey.md`](../../ROLE_EVIDENCE_Prashant_Chouksey.md) | Present; community links pending per file |
| Niraj Gupta | `ROLE_EVIDENCE_Niraj_Gupta.md` | Missing; Niraj must provide/verify Sales contributions and community links for Niraj's archive |

## Final upload gate

Before uploading Anil's archive:

1. Add genuine Anil community checkpoint/reply permalinks or permitted screenshots.
2. Commit all reviewed changes and wait for backend, frontend, and container CI success on that exact commit.
3. Run `make submission-zip` from a clean worktree.
4. Inspect `unzip -l dist/ClearSpend-Anil_Katta.zip` and the printed SHA-256 digest.
5. Open the ZIP once and confirm that `ClearSpend/ROLE_EVIDENCE_Anil_Katta.md` and the pitch PDF are present.
6. Upload the ZIP itself, not the source directory or a cloud shortcut.

