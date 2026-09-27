# Rubric evidence map

This is the assessor-facing index for the final ClearSpend bundle. It distinguishes implemented artifacts from qualitative evidence and unvalidated hypotheses. The row-level status is maintained in [`rubric-matrix.csv`](rubric-matrix.csv).

| Assignment area | Primary evidence | Current boundary |
|---|---|---|
| Working product and engineering | [`../../README.md`](../../README.md), [`../architecture/as-built-architecture.md`](../architecture/as-built-architecture.md), [`../adr/`](../adr/), [`../security/threat-model.md`](../security/threat-model.md), [`../operations/local-runbook.md`](../operations/local-runbook.md), source and tests | Implemented synthetic-data MVP; local Compose demo. Production identity, managed key management, operational alerting, and browser E2E remain pilot gaps. |
| Tests and verification | [`../engineering/verification.md`](../engineering/verification.md), backend tests, frontend tests, [`../../scripts/smoke.py`](../../scripts/smoke.py) | Record final clean-run output, environment, timestamp, and commit identifier with the submitted ZIP. |
| Real-user evidence and decision traces | [`../interviews/README.md`](../interviews/README.md), [`../interviews/research-insights.md`](../interviews/research-insights.md), [`customer-validation-register.md`](customer-validation-register.md), `INT-01` through `INT-05` | Three independent reimbursement-relevant qualitative records exist; no measured product outcome, willingness-to-pay result, or production claim. |
| Stakeholder interviews | [`../interviews/interview-guide.md`](../interviews/interview-guide.md), [`../interviews/interview-summaries.md`](../interviews/interview-summaries.md) | Anonymized summaries and consent statement are included; further direct product interviews remain needed. |
| Business Model Canvas | [`../product/business-model-canvas.md`](../product/business-model-canvas.md) | Complete hypothesis canvas with precommitted tests; tests have not yet been executed. |
| Pricing and go-to-market | [`../pricing.md`](../pricing.md), [`../sales/positioning.md`](../sales/positioning.md), [`../sales/competitive-analysis.md`](../sales/competitive-analysis.md), [`../sales/pricing-validation.md`](../sales/pricing-validation.md), [`customer-validation-register.md`](customer-validation-register.md) | The ₹25,000 paid-pilot offer and unit economics are hypotheses; no paid commitment or WTP result is claimed. |
| Roadmap | [`../product/roadmap.md`](../product/roadmap.md) | Evidence- and risk-sequenced plan; outcomes remain prospective. |
| Pitch and demo narrative | [`../../pitch-deck/ClearSpend_Pitch_Deck.pdf`](../../pitch-deck/ClearSpend_Pitch_Deck.pdf), [`../../pitch-deck/README.md`](../../pitch-deck/README.md), [`../../demo/DEMO_NARRATIVE.md`](../../demo/DEMO_NARRATIVE.md) | Deck and fallback demo materials exist; live rehearsal evidence should be retained if available. |
| Decisions and AI disclosure | [`../decision-log.md`](../decision-log.md), [`../ai-collaboration-disclosure.md`](../ai-collaboration-disclosure.md), [Prashant's spend log](prashant-ai-spend-log.md), [Diya's spend log](diya-ai-spend-log.md), [Anil's spend log](anil-ai-spend-log.md) | Diya's reported amount and Anil's transparent reconstruction are documented. Prashant declared tool use but not billed spend; Niraj has not declared usage. Reconcile billing-owner evidence before claiming a whole-team total. |
| AI/API/tool billing attestation | [`ai-spend-billing-attestation.md`](ai-spend-billing-attestation.md) | Separates billed/reported values from estimates and provides the owner-confirmation fields required for a final team total. |
| Quantified customer validation | [`customer-validation-register.md`](customer-validation-register.md) | Three relevant qualitative records exist; observed time-saved and willingness-to-pay results remain uncollected. |
| PM individual role evidence and responsibility split | [Diya](../../ROLE_EVIDENCE_Diya_Mondal.md), [Prashant](../../ROLE_EVIDENCE_Prashant_Chouksey.md) | Prashant's confirmation records interviews as his primary ownership and pricing/roadmap as Diya's, with shared findings. Original agreement date/community publication remain unverified; Engineering and Sales role-evidence records still need completion. |
| Community discussion | External LearnHouse Team 7 shared thread | The supplied thread is genuine external evidence. Include permitted direct links or screenshots in the final ZIP; do not claim absent weekly checkpoints or replies. |
| Submission hygiene | [`../submission-readiness-audit.md`](../submission-readiness-audit.md), [`../../README.md`](../../README.md) | Final ZIP must exclude secrets, `.env`, dependency caches, virtual environments, `node_modules`, and generated builds, and remain below the size limit. |

## Assessor reading order

1. Read the README and run/verify instructions.
2. Review the architecture, controls, and tests.
3. Inspect the interview synthesis, Business Model Canvas, pricing, and roadmap together; they intentionally label unvalidated claims.
4. Use the deck and demo narrative for the product presentation.
5. Review the role evidence, community-thread capture, decision log, and AI disclosure for individual and process evidence.
