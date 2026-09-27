# Role evidence — Diya Mondal

**Role:** Product Manager

## Accountable PM delivery

Diya's PM scope is problem framing, business model, user research, decision logging, and roadmap work, shared with the other PM as stated in [`docs/PROBLEM-STATEMENT.md`](docs/PROBLEM-STATEMENT.md).

| Area | Delivered contribution | Inspectable evidence |
|---|---|---|
| Problem framing and product scope | Defined ClearSpend as a narrow, trustworthy reimbursement-review workflow rather than a clone of Ramp or a broad spend-management platform. Identified evidence gaps, product metrics, validation gates, and explicit scope deferrals. | [`docs/product/ramp-alignment-assessment.md`](docs/product/ramp-alignment-assessment.md), [`docs/clearspend_ramp_alignment_review.md`](docs/clearspend_ramp_alignment_review.md) |
| Product and market research | Compiled the Ramp-focused research used to distinguish reusable product patterns from unsupported assumptions, covering product surface, reimbursement rails, domain model, AI, compliance, integrations, architecture, and build sequencing. | [`docs/ramp-research/`](docs/ramp-research/), especially [`sources.md`](docs/ramp-research/sources.md) |
| Pricing and commercial logic | Defined a hypothesis-labelled commercial path, price metric, value/safety and willingness-to-pay gates, unit-economics inputs, and rejected alternatives. The earlier pricing proposal remains historical; the current Canvas precommits a ₹25,000 paid-pilot offer for discovery rather than treating a price as validated. | [`docs/pricing.md`](docs/pricing.md), [`docs/product/business-model-canvas.md`](docs/product/business-model-canvas.md), and [`docs/decision-log.md`](docs/decision-log.md) |
| Business model and discovery plan | Produced a nine-block Business Model Canvas for the narrow reimbursement-review MVP. Explicitly separated confirmed product facts, qualitative evidence, and untested market claims; ranked riskiest beliefs; mapped the user-to-business value chain; and precommitted dated problem, usability, and paid-commitment tests with pass/fail guardrails. | [`docs/product/business-model-canvas.md`](docs/product/business-model-canvas.md) |
| User research and evidence handling | Consolidated scattered interview material into consent-safe, anonymized, role-based records. Distinguished independent product feedback from process discovery; corrected the frequent employee reimbursement submitter record from internal context to consented independent qualitative feedback; linked findings to product decisions. | [`docs/interviews/README.md`](docs/interviews/README.md), [`docs/interviews/interview-summaries.md`](docs/interviews/interview-summaries.md), [`docs/interviews/research-insights.md`](docs/interviews/research-insights.md) |
| Decision and submission traceability | Recorded product decisions and connected research/pricing artifacts to the rubric and submission-readiness review. | [`docs/decision-log.md`](docs/decision-log.md), [`docs/evidence/rubric-matrix.csv`](docs/evidence/rubric-matrix.csv), [`docs/submission-readiness-audit.md`](docs/submission-readiness-audit.md) |
| Live-product narrative | Produced a ZIP-friendly, evidence-linked live-demo script covering employee submission, the missing-evidence loop, deterministic and bounded-AI controls, human approval, accounting export, and the no-money-movement boundary. | [`demo/DEMO_NARRATIVE.md`](demo/DEMO_NARRATIVE.md), [`demo/receipts/README.md`](demo/receipts/README.md), [`README.md`](README.md) |

## Decisions and integrity boundaries

1. Keep the MVP focused on receipt-first reimbursement review with cited, deterministic policy checks and a human final decision; defer cards, payments, procurement, and autonomous financial actions.
2. Treat pricing, customer value, and willingness to pay as hypotheses until supported by paid pilots and measured outcomes.
3. Retain only consent-safe, anonymized qualitative interview summaries. Do not claim that process-discovery interviews establish product preference, willingness to pay, or quantified outcomes.
4. Do not represent an accounting CSV handoff as payment, reimbursement completion, ERP acceptance, or production readiness.

## Remaining PM gaps

The following work remains incomplete and is not represented as completed evidence:

- Three independent reimbursement-related sources are now recorded (I-01, I-04, and I-05), but additional direct reviewer/product-use evidence, quantified baseline/time-saved evidence, and willingness-to-pay evidence still need collection.
- The Business Model Canvas is complete as a hypothesis and test-plan artifact; its behavioral, usability, and paid-commitment evidence still needs collection. A final now/next/later roadmap and pitch-deck evidence remain required.
- Community checkpoint and constructive-response links are external to this ZIP and are intentionally not fabricated.
