# Ramp alignment release response

Date: 2026-09-15

## Implemented for the release MVP

| Assessment request | Implementation evidence | Release status |
|---|---|---|
| Receipt-first workflow | Authenticated 5 MB JPEG/PNG/PDF upload; encrypted quarantine; fail-closed ClamAV scan before parsing; deep structure/resource/active-content checks; private decrypted preview; Tesseract/pypdf extraction; editable employee confirmation | Implemented for synthetic MVP |
| Receipt evidence revisions | Immutable expense-to-receipt revision links, supersession pointers, one current association per report line, actor/time/hash metadata, auditor-visible history, and assessment input pinning | Implemented |
| Multi-receipt expense reports | Up to 20 same-category receipts in one approval boundary; per-line confirmation and matching; server-derived aggregate; append-missing or replace-bundle resubmission; line-level accounting export | Implemented |
| Untrusted-document guardrails | OCR prompt-injection patterns route to `UNKNOWN`/human review and prevent model invocation; AI remains tool-less and cannot approve, export, or reveal other tenants | Implemented; heuristic control |
| Deterministic receipt matching | Amount, INR currency, normalized merchant, and incurred-date comparison; mismatch/unreadable becomes `UNKNOWN` and `NEEDS_REVIEW` | Implemented |
| Reviewer explainability | Recommendation explicitly labelled non-decision; source, reason code, explanation, and pinned policy citation text shown | Implemented |
| Information request loop | Reviewer message plus requested fields; employee sees the request and resubmits for a new revision | Implemented |
| Post-decision handoff | Approval → `READY_TO_EXPORT`; human coding confirmation → downloadable CSV → `EXPORTED`; adapter failures persist as retryable `EXPORT_FAILED` records with sanitized code/detail | Implemented |
| Product instrumentation | Submission-to-decision, active review, information-request, override, fallback, citation, and export signals | Implemented; system signals only |
| Currency safety | New submissions are INR-only and policy thresholds are currency-aware/fail closed | Implemented |
| Idempotency authorization | Replays verify actor and canonical request hash; changed requests return 409 | Implemented |
| Reproducible dates | Immutable `submitted_at` drives submission-window evaluation across retries/revisions | Implemented |
| Concurrent audit allocation | Organization row is locked before sequence allocation | Implemented |
| Risk-path verification | Unit/property checks, PostgreSQL export-failure/retry and unpublished-outbox recovery tests, plus automated live two-receipt scan → aggregate/per-line assessment → information request → append only a missed third receipt → immutable bundle revision → reassessment → EICAR quarantine → cross-tenant denial → decision → three-line CSV → concurrent audit smoke | Implemented |

## Explicitly deferred

- Money movement, reimbursement payout, cards, AP, procurement, and general finance agents.
- QuickBooks/Xero selection until interviews establish the actual system of record; CSV is the evidence-neutral pilot contract.
- Mileage, multi-currency conversion, funds/budgets, GST extraction, and entity-aware accounting dimensions until customer evidence prioritizes them.
- Customer-data readiness gates still deferred: OIDC/MFA, PostgreSQL RLS, managed KMS/envelope-key rotation, retention/deletion automation, signed direct access, managed scanner/signature monitoring, vendor DPA, and external integrity anchoring.

## Honest remaining limitations

- OCR quality is not yet validated on a representative receipt corpus. Scanned PDFs without embedded text are marked unreadable rather than silently accepted.
- `EXPORTED` means a CSV was produced; it is not proof of ERP ingestion, payment, book close, or customer time savings.
- Product metrics from synthetic runs are engineering evidence, not customer validation.
- The audit list and expense list still need cursor pagination before sustained pilot volume.
