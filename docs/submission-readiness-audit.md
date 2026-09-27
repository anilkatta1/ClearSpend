# Assignment submission-readiness audit

**Audit date:** 2026-09-21  
**Scope:** all stated requirements reviewed; schedule dates intentionally excluded from acceptance.  
**Evidence rule:** a plan, outline, or empty template is not counted as completed customer evidence.

## Result

The engineering MVP is credible and reproducible, but the assignment is **not yet 100% submission-ready**. The architecture, bounded workflow, controls, tests, and local deployment are substantially implemented. The release blockers are mainly cross-functional: measured real-user outcomes, stakeholder interviews, roadmap, willingness-to-pay results, pitch deck, remaining role-evidence files, community-post records, and actual AI spend. The Business Model Canvas now exists as a hypothesis and test-plan artifact; it is not yet evidence-validated.

## Rubric coverage

| Rubric area | Status | Evidence present | Still required |
|---|---|---|---|
| Engineering/reliability/depth | Strong MVP | As-built architecture, ADRs, Compose, migrations/seed, CI, tests, smoke, threat model, runbook | Capture final clean-run/CI evidence. Browser E2E and production identity/KMS remain honest pilot gaps. |
| 3–5 real users and decision traces | Partial | Five consent-safe canonical records are indexed in [`interviews/README.md`](interviews/README.md); three are independent reimbursement-related sources (`INT-01`, `INT-02`, and `INT-05`). Hypothesis → evidence → decision traces are in [`interviews/research-insights.md`](interviews/research-insights.md). | Obtain additional direct reviewer/product-use observations, negative findings, and measured outcomes; do not treat process discovery as willingness-to-pay or quantified validation. |
| Stakeholder/client interviews | Partial | [`interviews/`](interviews/) contains a consent-safe guide, anonymized summaries, and synthesis; consent to share was received 18 September. | Conduct additional product interviews that probe objections and concrete changes; retain participant-summary confirmation where feasible. |
| Business Model Canvas | Partial | [`product/business-model-canvas.md`](product/business-model-canvas.md) contains all nine blocks, evidence links, ranked beliefs, a value chain, and precommitted tests. | Run the planned behavioral, usability, and paid-commitment tests; update evidence status without relabeling hypotheses as facts. |
| Pricing/GTM | Partial | Packaging, metric, assumptions, unit-economics model, rejected alternatives | Willingness-to-pay evidence and measured/quoted ranges. |
| Evidence-backed roadmap | Partial | Draft now/next/later ideas | Standalone roadmap where each item cites evidence/risk/dependency and an exit criterion. |
| Pitch deck/live narrative | **Blocked** | Outline only | Actual deck: problem, insight, demo, market, model, evidence, competition, roadmap, ask; rehearse live flow. |
| Individual ownership | **Blocked** | Git history/raw engineering evidence | One `ROLE_EVIDENCE_<name>.md` per learner with owned outputs, decisions, links/commits, contributions, gaps. |
| Community discussion | **Blocked unless external evidence exists** | Nothing found in repository | Three substantive checkpoints per person plus constructive response links/screenshots/exports. Do not fabricate. |
| Decision log/AI disclosure | Partial | Architecture decisions and disclosure exist | Interview-driven decisions/rejections and actual total AI spend; “not exposed” is not a final total. |

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
- Obtain the real AI/API/tool spend from billing owners and record it.

### PM — Diya Mondal and Prashant Chouksey

- Record how shared PM accountability is divided while both remain accountable.
- Use the five canonical consent-safe records in [`interviews/`](interviews/), then recruit direct reviewer/product-use participants for the precommitted tests, with consent and no private data in the repository.
- Assign evidence IDs; document hypothesis → evidence → decision and contradictions.
- Execute and update the Business Model Canvas test plan, and complete an evidence-sequenced now/next/later roadmap.
- Add interview-driven decisions/rejected alternatives to the decision log.
- Each PM supplies their own role-evidence file and community checkpoint/reply evidence.

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
