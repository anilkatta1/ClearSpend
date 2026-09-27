# Assignment submission-readiness audit

**Audit date:** 2026-09-21  
**Documentation consolidation:** 2026-09-27; PM attribution, canonical links and artifact status updated. No new customer-validation or live-run result is implied.
**Scope:** all stated requirements reviewed; schedule dates intentionally excluded from acceptance.  
**Evidence rule:** a plan, outline, or empty template is not counted as completed customer evidence.

## Result

The engineering MVP is substantial, but the assignment is **not yet 100% submission-ready**. The architecture, bounded workflow, controls, tests, and local deployment configuration are implemented; final clean-run evidence still needs to be archived. The Business Model Canvas, now/next/later roadmap, pitch deck and both PM role-evidence records exist. Remaining gaps include direct product-use observations, measured outcomes, willingness-to-pay results, roadmap gate execution, pitch rehearsal, Engineering/Sales role records, community-post evidence and whole-team AI spend. Existing interview summaries are qualitative evidence, and the Canvas remains a hypothesis and test-plan artifact.

## Rubric coverage

| Rubric area | Status | Evidence present | Still required |
|---|---|---|---|
| Engineering/reliability/depth | Strong MVP | As-built architecture, ADRs, Compose, migrations/seed, CI, tests, smoke, threat model, runbook | Capture final clean-run/CI evidence. Browser E2E and production identity/KMS remain honest pilot gaps. |
| 3–5 real users and decision traces | Partial | Five consent-safe canonical records are indexed in [`interviews/README.md`](interviews/README.md); three are independent reimbursement-related sources (`INT-01`, `INT-02`, and `INT-05`). Hypothesis → evidence → decision traces are in [`interviews/research-insights.md`](interviews/research-insights.md). The gaps and collection protocol are explicit in [`evidence/customer-validation-register.md`](evidence/customer-validation-register.md). | Observe representative employee and finance-reviewer product tasks, retain negative findings, measure comparable baseline/ClearSpend times, and record explicit responses to a priced offer. Do not treat process discovery as willingness-to-pay or quantified validation. |
| Stakeholder/client interviews | Partial | [`interviews/`](interviews/) contains a consent-safe guide, anonymized summaries, and synthesis; consent to share was received 18 September. | Conduct additional product interviews that probe objections and concrete changes; retain participant-summary confirmation where feasible. |
| Business Model Canvas | Partial | [`product/business-model-canvas.md`](product/business-model-canvas.md) contains all nine blocks, evidence links, ranked beliefs, a value chain, and precommitted tests. | Run the planned behavioral, usability, and paid-commitment tests; update evidence status without relabeling hypotheses as facts. |
| Pricing/GTM | Partial | Packaging, metric, assumptions, unit-economics model, rejected alternatives | Willingness-to-pay evidence and measured/quoted ranges. |
| Evidence-backed roadmap | Partial | [`product/roadmap.md`](product/roadmap.md) is a standalone now/next/later roadmap sequenced by discovery, commercial, security, and operational gates, each with dependencies and exit criteria. | Execute the gates and update the roadmap with observed evidence; do not treat planned tests as validation. |
| Pitch deck/live narrative | Partial | 11-slide [`pitch-deck/ClearSpend_Pitch_Deck.pdf`](../pitch-deck/ClearSpend_Pitch_Deck.pdf) and `.pptx`, deck source/readme, screenshots, and [`demo/DEMO_NARRATIVE.md`](../demo/DEMO_NARRATIVE.md). | Rehearse and record a live or fallback walkthrough; preserve the evidence/hypothesis labels in delivery. |
| Individual ownership | Partial | [Diya's role record](../ROLE_EVIDENCE_Diya_Mondal.md) and [Prashant's role record](../ROLE_EVIDENCE_Prashant_Chouksey.md) identify PM contributions and preserve Prashant's confirmation of the responsibility split. | Add Engineering/Sales role records and actual community evidence. The original PM agreement date and team-discussion publication remain unverified. |
| Community discussion | Partial external evidence | The external LearnHouse Team 7 thread contains early problem-hypothesis/exception discussion, Anil's role/hypothesis posts, and Diya's alignment post referring to `product/ramp-alignment-assessment.md`. | Preserve direct links or permitted screenshots in the final ZIP. The supplied thread does not yet visibly demonstrate three qualifying weekly checkpoints and constructive replies per learner; do not backdate or fabricate them. |
| Decision log/AI disclosure | Partial | Architecture/product decisions, Diya's reported USD 16.7903, Anil's transparent token-based estimate, Prashant's declared tool use, and a documented USD 203.7549 subtotal exist. Evidence classes and owner-attestation fields are recorded in [`evidence/ai-spend-billing-attestation.md`](evidence/ai-spend-billing-attestation.md). | Obtain billing-owner confirmation, add Prashant's billed amount and Niraj's usage declaration, and replace Anil's estimate with billed account data if it becomes available. |

## Engineering verification and precise claims

The local verification currently covers Ruff, mypy, backend tests, frontend lint/type/test, and Compose validation. Database-backed CI runs PostgreSQL integration tests; the container job builds the stack and executes the smoke journey. Final evidence should record commit SHA, CI URL, test count, environment, timestamp, and skips.

Architecture claims must stay precise:

- Policy evaluation is typed deterministic Python, not OPA.
- LangGraph is a bounded workflow, not a free-running agent swarm.
- AI is fake/deterministic by default; live model quality is unvalidated.
- `EXPORTED` means CSV generated, not ERP accepted or employee paid.
- Demo identity and environment-key encryption are not production OIDC/KMS.
- Telemetry is logs/correlation/health/audit/product metrics, not OpenTelemetry/Grafana.
- Multi-receipt reports support 1–20 line items and aggregate recommendation; this is not trip itinerary reconciliation or payment batching.

## Accountable-owner checklist

### Engineer — Anil Katta

- Keep the as-built architecture, ADRs, runbook, threat model, and limitations synchronized with code.
- Archive final `make verify`, database CI, and clean-stack `make smoke` results with commit SHA.
- Choose local-only or hosted demo explicitly. A hosted customer-data system additionally needs TLS, OIDC/MFA, secrets/KMS, backups/restore, monitoring/alerts, and rollback rehearsal.
- Add `ROLE_EVIDENCE_Anil_Katta.md` covering architecture, reliability/security, tests, deployment, telemetry, decisions, and cross-functional contributions.
- Build the ZIP from tracked files only; exclude `.env`, secrets, venvs, `node_modules`, caches, logs, and builds.
- Use [`evidence/ai-spend-billing-attestation.md`](evidence/ai-spend-billing-attestation.md) to obtain billing-owner confirmation for every contributor/tool; preserve Anil's reconstruction as an audit trail and replace its submitted amount with billed account data if available.

### PM — Diya Mondal and Prashant Chouksey

- Preserve the recorded split: Prashant owns interviews; Diya owns pricing and the roadmap; both share findings and retain PM accountability. Link actual team-discussion evidence when available; the original agreement date is not established by the current record.
- Use the five canonical consent-safe records in [`interviews/`](interviews/), then recruit direct reviewer/product-use participants for the precommitted tests, with consent and no private data in the repository.
- Assign evidence IDs; document hypothesis → evidence → decision and contradictions.
- Execute and update the Business Model Canvas test plan and the existing evidence-sequenced now/next/later roadmap. Do not treat the existence of these artifacts as successful validation.
- Add interview-driven decisions/rejected alternatives to the decision log.
- Maintain both PM role-evidence files and add actual community checkpoint/reply evidence. Record task boundaries, baseline and app handling times, waiting separately, receipt count, errors, corrections and unsuccessful observations before claiming savings.

### Sales — Niraj Gupta

- Run stakeholder/client interviews with a consistent script and consent-safe anonymized summaries.
- Test positioning, package, price metric, and willingness to pay; record respondent type, range, objections, and decision.
- Maintain an anonymized pipeline/stakeholder summary and competitive positioning.
- Own the pitch narrative and ask; show what interviews changed.
- Add the sales role-evidence file and community checkpoint/reply evidence.

### Whole team

- Use one terminology set: report/line item, recommendation/decision, ready-to-export/exported.
- Rehearse upload → assessment → review → information request/resubmission or export → auditor trace.
- Assign a speaker/operator and keep a tested fallback recording/screenshots.
- Link every pitch claim to code, automated evidence, or a clearly labeled hypothesis.
- Inspect the exact ZIP for privacy, secrets, licenses, reproducibility, and size.

## Definition of 100% done

Every required artifact exists in final form; every rubric row maps to inspectable evidence; all role/community records are present; customer claims come from consent-safe research; the exact submitted commit passes CI and the live journey; total AI spend is recorded; and each submitted ZIP is clean and reproducible.
