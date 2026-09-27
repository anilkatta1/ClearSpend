# Role evidence — Diya Mondal

**Role:** Product Manager

## Accountable PM delivery

Diya's PM scope is problem framing, business model, user research, decision logging, and roadmap work, shared with the other PM as stated in [`docs/PROBLEM-STATEMENT.md`](docs/PROBLEM-STATEMENT.md).

| Area | Delivered contribution | Inspectable evidence |
|---|---|---|
| Problem framing and product scope | Defined ClearSpend as a narrow, trustworthy reimbursement-review workflow rather than a clone of Ramp or a broad spend-management platform. Identified evidence gaps, product metrics, validation gates, and explicit scope deferrals. | [`docs/product/ramp-alignment-assessment.md`](docs/product/ramp-alignment-assessment.md), [`docs/clearspend_ramp_alignment_review.md`](docs/clearspend_ramp_alignment_review.md) |
| Product and market research | Compiled the Ramp-focused research used to distinguish reusable product patterns from unsupported assumptions, covering product surface, reimbursement rails, domain model, AI, compliance, integrations, architecture, and build sequencing. | [`docs/ramp-research/`](docs/ramp-research/), especially [`sources.md`](docs/ramp-research/sources.md) |
| Pricing and commercial logic | Defined a hypothesis-labelled commercial path, price metric, value/safety and willingness-to-pay gates, unit-economics inputs, and rejected alternatives. The earlier pricing proposal remains historical; the current Canvas precommits a ₹25,000 paid-pilot offer for discovery rather than treating a price as validated. | [`docs/pricing.md`](docs/pricing.md), [`docs/product/business-model-canvas.md`](docs/product/business-model-canvas.md), and [`docs/decision-log.md`](docs/decision-log.md) |
| Business model and discovery plan | Produced a nine-block Business Model Canvas for the narrow reimbursement-review MVP. It links the relevant consented interview evidence, separates confirmed product facts from qualitative evidence and market hypotheses, ranks riskiest beliefs, maps the user-to-business value chain, and precommits dated problem, usability, and paid-commitment tests with pass/fail guardrails. | [`docs/product/business-model-canvas.md`](docs/product/business-model-canvas.md), [`docs/interviews/README.md`](docs/interviews/README.md) |
| User research and evidence handling | Consolidated scattered interview material into five consent-safe, anonymized, role-based records. Distinguished direct product feedback from process discovery; corrected and reclassified the consented frequent employee submitter as independent qualitative feedback; linked findings to product decisions. | [`docs/interviews/README.md`](docs/interviews/README.md), [`docs/interviews/INT-01-employee-submitter.md`](docs/interviews/INT-01-employee-submitter.md), [`docs/interviews/INT-02-finance-reviewer.md`](docs/interviews/INT-02-finance-reviewer.md), [`docs/interviews/research-insights.md`](docs/interviews/research-insights.md) |
| Decision, roadmap, and submission traceability | Recorded product decisions and connected research/pricing artifacts to the rubric and submission-readiness review. Created a now/next/later roadmap sequenced by discovery, usability, paid-commitment, security, and operational gates. It explicitly records the current generic employee-only flow, the Excel/ticket-heavy logistics/relocation process, evidence-gated logistics workflow, and production authentication/RBAC requirements. | [`docs/decision-log.md`](docs/decision-log.md), [`docs/product/roadmap.md`](docs/product/roadmap.md), [`docs/evidence/rubric-matrix.csv`](docs/evidence/rubric-matrix.csv), [`docs/submission-readiness-audit.md`](docs/submission-readiness-audit.md) |
| Live-product narrative | Produced a ZIP-friendly, evidence-linked live-demo script covering employee submission, the missing-evidence loop, deterministic and bounded-AI controls, human approval, accounting export, and the no-money-movement boundary. | [`demo/DEMO_NARRATIVE.md`](demo/DEMO_NARRATIVE.md), [`demo/receipts/README.md`](demo/receipts/README.md), [`README.md`](README.md) |
| Pitch deck | Created an 11-slide, demo-integrated pitch deck covering the customer problem, product insight and workflow, MVP trust boundary, target segment and alternatives, evidence-labelled pilot model, roadmap, and design-partner ask. The deck explicitly distinguishes implementation facts, qualitative evidence, and unvalidated commercial hypotheses. | [`pitch-deck/ClearSpend_Pitch_Deck.pdf`](pitch-deck/ClearSpend_Pitch_Deck.pdf), [`pitch-deck/ClearSpend_Pitch_Deck.pptx`](pitch-deck/ClearSpend_Pitch_Deck.pptx), [`pitch-deck/README.md`](pitch-deck/README.md) |

## Decisions and integrity boundaries

1. Keep the MVP focused on receipt-first reimbursement review with cited, deterministic policy checks and a human final decision; defer cards, payments, procurement, and autonomous financial actions.
2. Treat pricing, customer value, and willingness to pay as hypotheses until supported by paid pilots and measured outcomes.
3. Retain only consent-safe, anonymized qualitative interview summaries. Do not claim that process-discovery interviews establish product preference, willingness to pay, or quantified outcomes.
4. Do not represent an accounting CSV handoff as payment, reimbursement completion, ERP acceptance, or production readiness.

## Remaining PM gaps

The following work remains incomplete and is not represented as completed evidence:

- Three independent reimbursement-related sources are now recorded: [`INT-01`](docs/interviews/INT-01-employee-submitter.md), [`INT-02`](docs/interviews/INT-02-finance-reviewer.md), and [`INT-05`](docs/interviews/INT-05-relocation-stakeholder.md). Additional direct reviewer/product-use evidence, quantified baseline/time-saved evidence, and willingness-to-pay evidence still need collection.
- The Business Model Canvas is complete as a hypothesis and test-plan artifact; its behavioral, usability, and paid-commitment evidence still needs collection. The now/next/later roadmap is documented in [`docs/product/roadmap.md`](docs/product/roadmap.md); the pitch deck is complete but its commercial and customer-outcome claims remain hypothesis-labelled.
- Community checkpoint and constructive-response links are external to this ZIP and are intentionally not fabricated.
