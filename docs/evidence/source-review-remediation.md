# Final source-review remediation

**Basis:** assignment rubric, source/workflow inspection and Niraj's instructions.
**Execution boundary:** Niraj reports that he previously tested the app and it ran
successfully. The precise date, command and source revision were not supplied. At his
request, the latest fixes were made without application startup, dependency installation
or test execution after that instruction. Earlier installation attempts failed; they
are not test failures. This document does not claim a fresh passing release.

## Changes made

| Review finding | Change | Evidence and remaining boundary |
|---|---|---|
| The report's earliest date could conceal a future-dated receipt. | Apply submission-window rules to each current receipt before optional AI, with line number, policy citation and receipt hash. Keep total-amount policy at report level. Use `EXPENSE_DATE_IN_FUTURE` for a future date. | [Assessment implementation](../../services/backend/app/services.py), [date regressions](../../services/backend/tests/unit/test_assessment_dates.py). Tests cover a mixed current/future report, an overdue line and the inclusive 30-day boundary through actual assessment orchestration. Added, not executed. |
| Audit hashes did not cover event timestamps. | New events include a server-owned format-2 marker in hashed metadata and a canonical UTC timestamp. Verification rejects changed timestamps, unknown formats, sequence gaps and later format downgrades. | [Audit implementation](../../services/backend/app/audit.py), [unit regressions](../../services/backend/tests/unit/test_audit.py), [PostgreSQL round-trip regression](../../services/backend/tests/integration/test_release_risk_recovery.py). Added, not executed. |
| A timestamp fix could invalidate existing history or falsely imply historical coverage. | Preserve legacy hashes and verify the legacy prefix using its original format. Report legacy-event count in the audit API and display the timestamp-coverage limitation in the UI. | No history rewrite or database migration. Legacy timestamps remain unprotected; an external integrity anchor is still deferred. |
| Backend dependency layer attempted to install the local package before its source was copied. | Install locked dependencies with `--no-install-project`, then install the project after copying source. | [Dockerfile](../../services/backend/Dockerfile). Source-reviewed; no image build executed. |
| Demo startup required manual environment setup and exposed demo services on all interfaces. | `make demo` creates the synthetic environment file only if absent. Bind web, API and MinIO ports to localhost. | [Makefile](../../Makefile), [Compose](../../compose.yaml). Existing environment settings remain intact. Containers were not started. |
| Community evidence and role/index summaries were stale. | Include the two captured responses and four additional messages Niraj confirmed publishing. Update role evidence and rubric references. Preserve the original posted wording and its time-of-post claims. | [Community record](../community.md). Actual URLs/timestamps and earlier weekly coverage are pending. |
| Earlier ZIP contained different billing figures and omitted community records. | Package the current canonical files, require the community and latest remediation evidence in the packager, and retain a billing-discrepancy ledger. | [Billing reconciliation](billing-reconciliation.md), [submission index](../../SUBMISSION_INDEX.md). Billing conflicts are disclosed, not resolved by choosing a higher or lower number. |
| Demo closing could be read as a measured speed claim. | Label faster review as an outcome hypothesis awaiting user measurement. | [Demo narrative](../../demo/DEMO_NARRATIVE.md). No new customer result is asserted. |

## Verification evidence by source

- **Author report:** Niraj says the earlier application ran successfully when he tested it.
- **Earlier recorded execution:** [reconciliation checks](reconciliation-checks.txt)
  retain CSV, retry and packaging regression results for the earlier source.
- **Static inspection:** the eight changed Python source/test/packaging files passed syntax parsing without importing or executing application code; [record and file hashes](source-inspection.txt). No TypeScript type check or container build was run.
- **Latest changes:** source review only. New tests are supplied for future execution;
  the existing CI configuration includes them through backend test discovery.
- **Packaging:** ZIP creation, file/link inspection and manifest checks concern the
  submission files only; they do not start or validate application behavior.

## Evidence that still requires people or external records

1. Original community post URLs and dates, especially any existing on-time weekly posts.
2. Relevant real-user task observations and honest negative findings; keep actual dates.
3. Interview-session ownership and clarification of INT-01's team relationship.
4. Responses to the exact pilot offer, including rejections and stated objections.
5. Confirmed contributor billing periods, amounts, allocation and overlap.
6. The PMs' agreed division of responsibilities recorded in the team discussion.

These gaps cannot be replaced by additional generated prose. No score increase is
certified by this document; it makes the revised implementation and evidence reviewable.
