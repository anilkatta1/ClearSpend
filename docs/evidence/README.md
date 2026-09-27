# Rubric evidence map

This is the assessor-facing index for the final ClearSpend bundle. It distinguishes implemented artifacts from qualitative evidence and unvalidated hypotheses. The row-level status is maintained in [`rubric-matrix.csv`](rubric-matrix.csv).

| Assignment area | Primary evidence | Current boundary |
|---|---|---|
| Working product and engineering | [`../../README.md`](../../README.md), [`../architecture/as-built-architecture.md`](../architecture/as-built-architecture.md), [`../adr/`](../adr/), [`../security/threat-model.md`](../security/threat-model.md), [`../operations/local-runbook.md`](../operations/local-runbook.md), source and tests | Implemented synthetic-data MVP; local Compose demo. Production identity, managed key management, operational alerting, and browser E2E remain pilot gaps. |
| Tests and verification | [`../engineering/verification.md`](../engineering/verification.md), backend tests, frontend tests, [`../../scripts/smoke.py`](../../scripts/smoke.py) | Targeted CSV/retry checks are recorded in [remediation evidence](submission-remediation.md). Niraj reports a successful earlier application test. The latest date-policy and timestamp changes were reviewed from source only; their new tests are unexecuted. See [source-review remediation](source-review-remediation.md). |
| Real-user evidence and decision traces | [`../interviews/README.md`](../interviews/README.md), [`../interviews/research-insights.md`](../interviews/research-insights.md), `INT-01` through `INT-06`, [participant/activity register](../interviews/evidence-register.md) | Six qualitative summaries: four reimbursement-related perspectives, three direct product-feedback participants and an explicit export-format objection. No measured product outcome or willingness-to-pay result is claimed. |
| Stakeholder interviews | [`../interviews/interview-guide.md`](../interviews/interview-guide.md), [`../interviews/interview-summaries.md`](../interviews/interview-summaries.md) | Anonymized summaries and consent statement are included; further direct product interviews remain needed. |
| Business Model Canvas | [`../product/business-model-canvas.md`](../product/business-model-canvas.md) | Complete hypothesis canvas with precommitted tests; tests have not yet been executed. |
| Pricing and go-to-market | [`../pricing.md`](../pricing.md), [`../sales/positioning.md`](../sales/positioning.md), [`../sales/competitive-analysis.md`](../sales/competitive-analysis.md), [`../sales/pricing-validation.md`](../sales/pricing-validation.md) | The ₹25,000 paid-pilot offer and unit economics are hypotheses; no paid commitment or WTP result is claimed. |
| Roadmap | [`../product/roadmap.md`](../product/roadmap.md) | Evidence- and risk-sequenced plan; outcomes remain prospective. |
| Pitch and demo narrative | [`../../pitch-deck/ClearSpend_Pitch_Deck.pdf`](../../pitch-deck/ClearSpend_Pitch_Deck.pdf), [`../../pitch-deck/README.md`](../../pitch-deck/README.md), [`../../demo/DEMO_NARRATIVE.md`](../../demo/DEMO_NARRATIVE.md) | Deck and fallback demo materials exist; live rehearsal evidence should be retained if available. |
| Decisions and AI disclosure | [`../decision-log.md`](../decision-log.md), [`../ai-collaboration-disclosure.md`](../ai-collaboration-disclosure.md) | Niraj reports USD 23.47, backed by [`niraj-ai-spend-log.md`](niraj-ai-spend-log.md). The [billing ledger](billing-reconciliation.md) records conflicting historical Niraj figures and an older reported Diya figure, with attribution and overlap pending. Billing scope/overlap and remaining team costs still need reconciliation; runtime USD 0.00 is not the team total. |
| Niraj's individual role evidence | [Sales role evidence](../../ROLE_EVIDENCE_Niraj_Gupta.md) | Standalone Sales responsibilities, commercial decisions, supported remediation direction, two captured comments and four author-confirmed published posts; historical interview attribution remains to be confirmed. |
| Community discussion | [Team 7 collaboration traces](../community.md), [original supplied excerpt](community-thread-excerpt.txt) | Two Niraj responses are inspectable in the original supplied text and four additional posts are confirmed published by Niraj, with hypotheses, constructive challenges and positioning decisions. Original URLs, absolute dates and three distinct weekly checkpoints remain unestablished. |
| Submission hygiene | [`../submission-readiness-audit.md`](../submission-readiness-audit.md), [`../../README.md`](../../README.md) | Final ZIP must exclude secrets, `.env`, dependency caches, virtual environments, `node_modules`, and generated builds, and remain below the size limit. |

## Assessor reading order

1. Read the README and run/verify instructions.
2. Review the architecture, controls, and tests.
3. Inspect the interview synthesis, Business Model Canvas, pricing, and roadmap together; they intentionally label unvalidated claims.
4. Use the deck and demo narrative for the product presentation.
5. Review the role evidence, community-thread capture, decision log, and AI disclosure for individual and process evidence.
