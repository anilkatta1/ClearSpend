# ClearSpend business model canvas

**Product:** ClearSpend — a human-in-the-loop reimbursement-evidence review and accounting-handoff tool for organizations with receipt-based employee expenses.

**Stage:** MVP / pilot hypothesis. Product scope is deliberately limited to evidence capture, policy-aware human review, auditability, and CSV handoff; it does not issue cards, pay reimbursements, or replace an ERP.

## 1. Customer segments

- **Economic buyer:** Finance controller, finance-operations lead, or CFO at a small or mid-sized organization with recurring employee reimbursements.
- **Primary users:** Finance reviewers and accountants who validate receipts and prepare accounting entries.
- **Submitting users:** Employees incurring business expenses.
- **Influencers / risk approvers:** Auditors, operations leaders, IT/security, and budget owners.
- **Initial beachhead:** India-based, INR-only organizations handling multi-receipt travel or operating-expense claims through email, spreadsheets, tickets, or generic expense forms.

## 2. Value propositions

- One evidence packet for a complete expense report: receipt previews, employee-confirmed details, policy citations, checks, recommendation, and decision history in one place.
- Reduce repetitive reviewer work caused by downloading receipts and reconciling evidence across separate tools.
- Keep accountability with a finance reviewer: AI is bounded advisory assistance, while deterministic checks and human decisions remain visible.
- Preserve an audit-ready, immutable history of evidence changes, assessments, decisions, overrides, and exports.
- Resolve missing evidence within the same case instead of restarting the report.
- Provide a low-commitment accounting handoff through a line-level CSV, without requiring an ERP integration or payment-system replacement.

## 3. Channels

- Founder-led outreach to finance-operations leaders and controllers in the target segment.
- Design-partner pilots sourced through professional finance, startup, and local-business networks.
- Demonstrations using a prospect's existing reimbursement workflow and anonymized sample receipts.
- Content and referrals focused on auditability, policy compliance, and reviewer workflow—not autonomous finance.
- Later: accounting firms, ERP implementers, and HR/payroll consultants as referral or implementation partners.

## 4. Customer relationships

- High-touch onboarding: configure policy versions, categories, reviewers, accounting-code conventions, and migration of the active queue.
- Pilot success plan with weekly feedback and review of operational metrics.
- Role-specific support for employees, reviewers, and auditors.
- Shared responsibility model: ClearSpend provides evidence and workflow controls; the customer retains policy ownership, approval authority, accounting posting, and payment.
- Trust through transparent recommendations, policy citations, exception handling, and export/audit records.

## 5. Revenue streams

- **Pilot:** a fixed-fee, time-boxed implementation and evaluation engagement. The precommitted discovery offer is ₹25,000 INR, paid in advance; it is not waived or counted as demand when free.
- **Recurring SaaS (hypothesis):** organization platform fee plus a per-active-reviewer or per-submitted-report fee.
- **Implementation services:** paid policy configuration, historical-data import, SSO/ERP integration, and compliance/security review for larger customers.
- **Expansion (only after validation):** premium audit retention/reporting, ERP connectors, advanced approval routing, and additional reimbursable-expense categories.

**Pricing principle:** price against finance-review effort, audit/rework risk, and workflow fragmentation—not against payment volume. Validate willingness to pay before publishing price points.

## 6. Key resources

- Secure reimbursement-review application, workflow engine, and encrypted receipt storage.
- Policy-rule model, deterministic matching, and bounded AI-assistance/evaluation capability.
- Audit-event chain and export records.
- Finance-operations domain expertise and policy-configuration playbooks.
- Customer research, pilot relationships, and trust/security evidence.
- Engineering, security, and customer-success capacity.

## 7. Key activities

- Acquire, onboard, and support design partners.
- Maintain secure receipt ingestion, malware scanning, extraction, evidence matching, and human-review workflow.
- Configure and version customer policies; improve explainability and exception handling.
- Measure reviewer time, information requests, overrides, errors, and export outcomes during pilots.
- Operate security, tenant isolation, auditability, backups, incident response, and privacy/retention controls.
- Validate pricing, implementation repeatability, and integration demand before broadening scope.

## 8. Key partners

- Cloud hosting, managed database/object storage, key-management, malware-scanning, and observability providers.
- OCR/document-extraction and AI providers, with fallbacks and contractual data protections.
- Accounting firms, fractional-CFO networks, and ERP/payroll consultants for distribution and workflow expertise.
- Early design partners supplying consented workflow feedback and pilot evaluation.
- Security/compliance advisors and, later, identity/SSO and ERP integration partners.

## 9. Cost structure

- Product engineering, QA, security, and operations.
- Cloud compute, encrypted storage, database, backup, monitoring, scanning, OCR, and AI inference.
- Customer onboarding, policy configuration, support, and pilot success work.
- Security/compliance activities: penetration testing, audits, legal/privacy review, insurance, and incident readiness.
- Sales, partner development, and customer research.

## Assumptions to test before scaling

| Assumption | Evidence today | Pilot test / success signal |
|---|---|---|
| A unified evidence packet reduces reviewer effort. | Qualitative support from an independent finance reviewer ([`INT-02`](../interviews/INT-02-finance-reviewer.md)) and a frequent submitting user ([`INT-01`](../interviews/INT-01-employee-submitter.md)); not measured. | Compare reviewer time and external downloads/lookups for comparable claims. |
| Finance teams will pay for this narrow workflow without payment or ERP integration. | Not yet validated. | Test paid-pilot conversion and willingness-to-pay interviews with economic buyers. |
| CSV is sufficient for an initial accounting handoff. | Product decision; no customer validation. | Track export completion, manual CSV rework, and requests for specific integrations. |
| Human-reviewed, explainable assistance creates more trust than automation-first tools. | Strong design constraint; limited direct feedback. | Measure recommendation use, override reasons, and reviewer trust feedback. |
| INR-only multi-receipt claims are a viable beachhead. | Current MVP boundary, not market proof. | Recruit 3–5 independent target organizations and measure claim volume and pain intensity. |

## Evidence status and discovery boundary

This is a **hypothesis canvas**, not a validated business model. Product capabilities described in the README are `CONFIRMED` implementation facts. The five consented, anonymized interview records in [`docs/interviews`](../interviews/README.md) are qualitative `EVIDENCE`; they do not establish frequency, time saved, willingness to pay, or repeatable demand. All market, pricing, segment, channel, and business-value claims below remain `HYPOTHESES` until tested.

**Stage gate:** Customer Discovery is incomplete. Customer Validation has not started, and broad scaling is prohibited until a fresh, minimally assisted cohort reaches the precommitted validation gate below.

## Riskiest-belief ledger

| Rank | Mechanism | One atomic belief | Evidence today | Consequence if false | Next decision |
|---|---|---|---|---|---|
| 1 | Viability | Economic buyers will make a paid commitment for a reimbursement-review workflow before ERP integration or payments exist. | No willingness-to-pay evidence. | High: no sustainable business despite usable product. | Test paid-pilot commitment before building connectors or broadening scope. |
| 2 | Value | Finance reviewers handling recurring multi-receipt claims experience enough fragmented-evidence work to change their workflow. | One direct qualitative reviewer interview ([`INT-02`](../interviews/INT-02-finance-reviewer.md)), corroborated by a frequent submitting user ([`INT-01`](../interviews/INT-01-employee-submitter.md)) and reimbursement-related process discovery ([`INT-05`](../interviews/INT-05-relocation-stakeholder.md)). | High: the unified packet is convenience, not a compelling job. | Observe recent claims and their existing workaround with target reviewers. |
| 3 | Usability | A reviewer can make a defensible decision from the packet without increasing policy or evidence mistakes. | Product has engineering tests, not independent usability evidence. | High: adoption and trust fail; risk rises. | Run realistic, unassisted review tasks with representative claims. |
| 4 | Feasibility / institutional | A pilot customer can permit secure receipt processing and provide the policy, access, and accounting workflow required for use. | Technical controls exist; customer security/legal acceptance is untested. | High: pilots cannot launch. | Complete security review and data-processing/access check with each candidate. |

## Explicit value-chain hypothesis

| Link | Current claim | How it will be observed |
|---|---|---|
| User struggle | Reviewers reconstruct receipt, policy, and prior-decision evidence across tools. | Contextual walkthrough of a recent claim and its artifacts. |
| Intervention | ClearSpend presents the complete evidence packet, deterministic checks, policy citations, and decision history together. | Eligible report opened in ClearSpend. |
| Behavior change | Reviewer uses the packet rather than downloading receipts or searching separate policy/approval sources. | Per-report external lookup/download count and reviewer task trace. |
| Operational effect | A reviewer reaches a decision with less avoidable evidence-gathering delay. | Median active review time and median submission-to-decision time per eligible report. |
| Single business lever | **Speed** — a decision reaches the accounting-handoff step sooner. | Submission-to-decision duration; verify that CSV/accounting handoff starts earlier rather than merely moving the queue. |
| Weakest arrow | Reduced external lookups may not reduce total decision time or matter to the buyer. | Compare matched claim types against the current workflow; collect the buyer's view of materiality. |

Do not claim labor-cost savings unless measured saved time is demonstrably convertible into reduced labor, contractor, or support cost.

## Precommitted discovery tests

These test cards are precommitted on **2026-09-27**, before outreach. The accountable product lead owns the tests. Dates, price, measures, and decision rules below must not be changed after recruitment begins.

**Paid-pilot offer:** **₹25,000 INR**, paid in advance and non-refundable, for a 30-calendar-day pilot with one organization, up to 10 active reviewers, configured reimbursement-policy workflow, and CSV accounting handoff. It excludes custom ERP integrations, payment execution, SSO, and production-security commitments beyond the documented MVP scope.

| Belief | Test window / target and method | Observable measure | Pass / inconclusive / fail | Guardrail and decision |
|---|---|---|---|---|
| Recurring fragmented review is a material problem. | **2026-10-05 to 2026-10-16.** Five finance reviewers who personally completed at least three receipt-based reimbursement reviews in the preceding 90 days; contextual walkthrough of one recent claim and its actual artifacts. | Participants showing a repeated workaround: ≥2 separate evidence sources or a receipt download/search beyond their core workflow. | Pass: ≥3/5; inconclusive: 2/5; fail: ≤1/5. | No customer receipts retained without written consent. Pass → usability test; inconclusive → narrow segment; fail → reframe or stop. |
| The packet improves review behavior without harming decision quality. | **2026-10-19 to 2026-10-30.** At least six reviewers across three target organizations complete unassisted, counterbalanced reviews of 12 matched, de-identified claims in their current workflow and ClearSpend. | Median active review time; external evidence lookups; independently checked decision/coding errors. | Pass: ClearSpend median active-review time is ≥20% lower, external lookups do not increase, and material decision/coding errors do not increase. Inconclusive: 0–19% time reduction with guardrails clear. Fail: no reduction, slower review, or any error increase. | Any material security, authorization, or incorrect autonomous-decision incident pauses the test. Pass → paid-pilot offer; otherwise reshape workflow. |
| Buyers will pay for the narrow MVP. | **2026-11-02 to 2026-11-13.** Five economic buyers meeting the target criteria receive the same ₹25,000 paid-pilot offer after the workflow demonstration; record every acceptance and rejection. | Signed paid-pilot agreement, purchase order, or ₹25,000 payment—not stated interest. | Pass: ≥2/5 paid commitments; inconclusive: 1/5; fail: 0/5. | No free pilot, non-binding LOI, or verbal interest is counted as demand. Pass → begin a paid pilot by 2026-11-30; otherwise revise the segment/value proposition or stop. |

## Validation and scale gate

Customer Validation begins only after Discovery produces behavioral evidence and at least one paid commitment. Scale only when a **fresh**, minimally assisted cohort reaches activation through the intended channel, uses the workflow repeatedly for the agreed evaluation period, clears the safety guardrail, and produces revenue exceeding directly attributable onboarding and support costs. The cohort size, period, activation definition, retention definition, and unit-economics threshold must be fixed before validation begins.

## North-star outcome and pilot metrics

**North-star outcome:** a finance reviewer can reach a defensible reimbursement decision from one complete, traceable evidence packet.

Track: time from submission to decision; reviewer active time per report; external receipt downloads/lookups; information-request and resubmission rate; recommendation override rate and reason; export completion/failure; audit retrieval time; pilot retention; and paid-pilot conversion.
