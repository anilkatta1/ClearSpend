# ClearSpend product roadmap — Now / Next / Later

**Product boundary:** ClearSpend is a human-in-the-loop reimbursement-evidence review and accounting-handoff tool. It is not a payments, card, AP, procurement, or autonomous-approval product.

**Current gap:** the MVP has one generic employee reimbursement flow. It does not yet support a distinct employee-logistics/relocation flow (for example, approved cap, approved-vendor and proof-of-payment checks, and multi-role review). In the observed logistics process, evidence and reconciliation are largely manual and spread across Excel files, tickets, and attachments. The demo role selector is not authentication; production OIDC/MFA and enforceable RBAC are still required.

**Planning principle:** sequence work by the riskiest unproven belief and its dependency, not by feature appeal. The receipt-first review loop and CSV handoff are implemented for the synthetic MVP; customer value, demand, and production readiness are not yet validated.

## Now — establish whether the narrow workflow is valuable and purchasable

**Objective:** learn whether finance reviewers have a material fragmented-evidence problem and whether the complete evidence packet improves a defensible decision.

| Work | Why now / dependency | Evidence or exit gate |
|---|---|---|
| Run five contextual walkthroughs with finance reviewers and logistics/relocation stakeholders (5–16 Oct 2026). Observe a recent reimbursement review, including the Excel, ticket, and attachment handoffs where applicable. | The material-problem belief and the need for a separate logistics flow are unproven; integration and workflow expansion would be premature. | At least 3/5 participants show a repeated workaround involving two or more evidence sources or an extra receipt download/search. Record whether logistics needs an approved cap, vendor/proof checks, or additional approvers. If 2/5, narrow the segment; if 1/5 or fewer, reframe or stop. |
| Run an unassisted, counterbalanced usability test with at least six reviewers across three target organizations (19–30 Oct). Include representative employee and logistics/relocation cases only when their workflows differ. | Must establish behavior and safety before asking buyers to pay or building role-specific workflows. | ClearSpend reduces median active review time by at least 20%, does not increase external lookups, and causes no increase in material decision/coding errors. Otherwise reshape the workflow rather than add features. |
| Instrument and review the core funnel: submission-to-decision time, active review time, external lookups/downloads, information requests, overrides, fallbacks, and export outcomes. | Existing telemetry is synthetic engineering evidence; the value claim needs comparable task evidence. | Produce a consent-safe result record for every task, including errors, objections, and a keep/change/reject decision. |
| Make the MVP safe for de-identified discovery use: document the data boundary, distinguish demo roles from real access control, and resolve test-blocking defects. | Real receipts and a production claim are out of scope until security acceptance is earned; the current header-selected identity is not authentication or sufficient RBAC. | No participant data is retained without written consent; no material authorization, tenant-isolation, or autonomous-decision incident occurs. |

**Now decision:** only offer the paid pilot if the usability gate passes. If it does not, use observed friction to narrow or redesign the evidence packet, not to broaden into ERP, payment, or AI features.

## Next — test commercial commitment and pilot repeatability

**Entry condition:** Now demonstrates better review behavior without a safety or quality regression.

| Work | Why next / dependency | Evidence or exit gate |
|---|---|---|
| Present the identical ₹25,000 INR, paid-in-advance 30-day pilot offer to five qualified economic buyers (2–13 Nov 2026). | Willingness to pay is the highest viability risk and cannot be inferred from interviews or free use. | At least 2/5 paid commitments (agreement, PO, or payment) → begin a paid pilot by 30 Nov. One is inconclusive; zero means revise the segment/value proposition or stop. |
| Onboard the committed pilot with one policy, review roles, and the CSV handoff; define its baseline, success measures, and support cost before use begins. | A customer-specific configuration is necessary to test repeat use, but custom integrations would obscure the MVP test. | A written pilot scorecard covers active review time, policy/coding errors, export completion/rework, support hours, and the customer’s accounting handoff. |
| Implement production authentication and RBAC before any pilot handles live customer data. Replace the demo identity selector with OIDC/MFA, server-enforced organization/role permissions, and auditable access decisions. | Employees, logistics stakeholders, reviewers, accountants, and auditors require different access; UI-only/demo roles do not protect financial evidence. | Role-permission matrix approved by the design partner; authorization and tenant-isolation tests cover every protected workflow; security review accepts the pilot boundary. |
| Build a separate logistics/relocation workflow only if discovery confirms it is a recurring, high-value variant. Start with a configured approved cap, approved-vendor/proof-of-payment evidence, logistics/operations review, and an Excel-compatible import/export boundary. | The present employee flow cannot assume the logistics process, but a bespoke flow before evidence would be feature-led. | Target participants confirm the distinct steps; a design partner commits to test the workflow; task testing shows it reduces Excel/ticket handoffs without raising decision errors. |
| Validate the accounting handoff rather than assume CSV is sufficient. | The current export proves generation, not ERP ingestion, reconciliation, or customer value. | Observe accountant use and track export completion, manual rework, error categories, and requests for a system of record. Choose CSV hardening or one integration only from this evidence. |
| Remove pilot-volume and live-data blockers as required by the design partner: RLS, managed key management/rotation, retention/deletion, signed object access, scanner monitoring, and pagination. | These controls precede any live customer-data claim; they are not differentiating features. | Security and data-processing review accepted for the agreed pilot boundary, with incident/operational ownership documented. |

**Next decision:** continue only when a pilot has repeat use, no material safety or policy-quality failure, and revenue greater than directly attributable onboarding and support cost. A connector is an evidence-gated follow-on, not a default commitment.

## Later — deepen the proven wedge, then selectively expand

**Entry condition:** a fresh, minimally assisted cohort repeatedly activates through the intended channel, clears safety guardrails, and meets the precommitted unit-economics threshold.

| Investment | Triggering evidence | Intended outcome |
|---|---|---|
| Harden the reimbursement-review product: policy configuration, audit retrieval/reporting, exception workflows, and operating reliability. | Repeated pilot use shows the review workflow—not a missing adjacent module—is the bottleneck. | A repeatable, supportable evidence-review product. |
| Build one accounting integration behind a generic, idempotent export contract. | Accountants show that CSV rework or a named system of record blocks adoption; one connector has clear demand. | Handoff without rekeying, with actionable sync recovery. |
| Add reimbursement variants such as mileage, multi-currency, GST evidence, or entity/cost-center dimensions. | Observed claim mix demonstrates that a specific missing variant excludes the beachhead. | Broader coverage without weakening the current decision/audit boundary. |
| Add configurable approval routing or budget context. | Multiple design partners show that the present single reviewer decision cannot fit their workflow—particularly logistics/relocation cases requiring operations or budget-owner review—and commit to the capability. | More organizations can use the same trusted review loop. |

## Explicitly not on this roadmap

Cards, banking, reimbursements/payouts, AP, procurement, treasury, general finance chatbots, autonomous approvals, and agent payments remain deferred. They introduce different regulated workflows and should not be reconsidered unless research shows the reimbursement-review wedge is validated and a specific adjacent job is the binding adoption constraint.

## Ownership and review cadence

The PM owners maintain the evidence ledger and make keep/change/reject decisions after each gate. Engineering owns release, security, operational, and measurement readiness. Sales owns qualified buyer recruitment and records the exact commercial offer and outcome. Review this roadmap after each test window; changes must cite new evidence in the decision log.

## Source artifacts

- [Business Model Canvas](business-model-canvas.md): precommitted discovery tests, paid-pilot offer, and scale gate.
- [Research insights](../interviews/research-insights.md): qualitative evidence and its limits.
- [Ramp alignment release response](ramp-release-response.md): implemented scope and deferred boundaries.
- [Known limitations](../known-limitations.md): production-readiness gaps.
- [Decision log](../decision-log.md): decisions and rejected alternatives.
