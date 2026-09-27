# Research insights: reimbursement evidence and review

**Sources:** [I-01–I-05](README.md) in [`interview-summaries.md`](interview-summaries.md).  
**Consent:** anonymized sharing consent received 18 September.

## What we heard

| Finding | Supporting evidence | Confidence / boundary |
|---|---|---|
| Reviewers and submitters reconstruct or repeatedly provide the same evidence when receipts, budget context, prior decisions, and policy live in separate places. | I-01 and I-05; corroborating process patterns in I-02 and I-04 | Qualitative; no time measurement |
| A reviewer benefits from viewing receipts, policy context, recommendation, and decision history together. | I-01 | Direct product feedback from one finance reviewer |
| Human approval remains necessary for ambiguous evidence and organizational accountability. | I-01 and I-05; approval patterns in I-02–I-04 | Strong design constraint, not proof of preferred approval-chain configuration |
| Missing evidence should continue an existing case rather than force a restart. | I-01 and I-05 | Direct qualitative product feedback from a finance reviewer and a frequent submitting user |
| Authorization, verification, and reconciliation must remain traceable. | I-02–I-04 | Adjacent process discovery; ClearSpend currently covers only the reimbursement-review portion |

## Hypothesis → evidence → decision

| ID | Hypothesis | Evidence | Decision |
|---|---|---|---|
| D-01 | A unified evidence packet reduces avoidable reviewer effort and submitter rework. | I-01 and I-05 described repeated receipt, policy, and approval-context work; I-02/I-04 show evidence and approvals are distributed across tools. | Keep receipt previews, deterministic checks, policy citations, recommendation, and decision history in the reviewer flow. |
| D-02 | Inline receipt preview is operationally meaningful. | I-01 explicitly preferred in-product preview to repeated downloads. | Retain inline/modal preview with authorization and audit checks. |
| D-03 | Visible policy context improves trust in assistance. | I-01 valued direct policy visibility; I-02/I-04 depend on budget/policy controls. | Show pinned policy citations, reasons, and check status; do not present a bare approve/reject score. |
| D-04 | Evidence gaps should be resolved in the same case. | I-01 valued requesting and appending missing evidence without restarting. | Preserve information-request → resubmission and immutable receipt revision behavior. |
| D-05 | The MVP must not claim to replace enterprise approval, procurement, budget, or payment systems. | I-02–I-04 describe organization-specific controls beyond reimbursement review. | Keep the scope to human-reviewed reimbursement evidence and accounting CSV handoff; label integrations and multi-stage approvals as future validation. |

## Future implications from process discovery

| Source area | Potential extension | Current boundary |
|---|---|---|
| Operations expenses (I-02) | Project/cost-centre coding, cumulative budget tracking, variance alerts, and staged approvals. | Current policy amount limits are not a budget ledger; ClearSpend does not map projects, calculate profitability, or implement organizational approval chains. |
| Relocation reimbursement (I-04) | Eligibility/offer-linked entitlements, approved-vendor checks, pre-approval evidence, and HR/operations/finance routing. | The generic reimbursement flow does not verify relocation eligibility, validate vendors, prove payment, or disburse reimbursements. |
| IT procurement (I-03) | A separately scoped requisition, quotation, PO/invoice/delivery matching, asset-tracking, and debit/credit-note module. | These are reusable evidence and audit-control patterns, not implemented ClearSpend procurement features. |

## Prashant's research-to-product recommendations

Prashant contributed the operations, IT procurement and relocation discovery material and the mapping below; see [his role evidence](../../ROLE_EVIDENCE_Prashant_Chouksey.md). Canonical records use anonymized IDs. These are recommendations derived from existing research, not additional interviews or proof that each interview caused a shipped change.

- **Operations — [INT-03](INT-03-head-of-operations.md):** spreadsheet budgets, ticket-based requisitions, project-cost mapping and multi-role sign-off suggest validating project/cost-center dimensions, staged approvals and variance review. The current product supplies receipt evidence, policy checks, a human decision and CSV coding; its amount limits are not a cumulative budget ledger and it does not calculate project profitability or budget variance.
- **Relocation — [INT-05](INT-05-relocation-stakeholder.md):** onboarding caps, approved vendors, itemized invoices, proof of payment and multi-role review suggest validating entitlement, vendor eligibility and supporting pre-approval evidence separately. Generic report submission and corrections cover shared steps, but ClearSpend does not implement relocation eligibility, HR/operations routing, payment verification or disbursement.
- **IT procurement — [INT-04](INT-04-it-head.md):** purchase requests, quotations, purchase orders, delivery inspection and debit/credit-note reconciliation require a separately scoped workflow. Receipt security, human review and audit history are reusable control patterns; they do not establish a delivered procurement or asset-management module.

The [roadmap](../product/roadmap.md#research-derived-enhancement-details) carries the evidence gates for these proposals. Broader ERP transition remains outside the committed reimbursement roadmap. Generalized canonical summaries take precedence over identifying details or organization-specific numerical thresholds in earlier drafts.

## What this does *not* establish

- It does not establish a quantified time saving, willingness to pay, production readiness, or an optimal approval hierarchy.
- I-02–I-04 are workflow-discovery interviews, not ClearSpend product tests.
- I-05 is independent qualitative feedback from a frequent submitting user, not a quantitative outcome study or a commitment to buy.
- The evidence contains three independent reimbursement-related sources (I-01, I-04, and I-05), but still needs more direct reviewer/product-use evidence, including negative findings and adoption objections.

## Next research

1. Test active reviewer time, external lookups/downloads, information-request rate, and time to final decision with at least three relevant independent users.
2. Ask finance, budget owners, and auditors about exceptions, approval-chain configuration, budget-system evidence, retention/export needs, security concerns, and willingness to pay.
3. Record each result with an evidence ID, anonymized role, consent status, contradiction or objection, and the resulting keep/change/reject decision.
4. For comparable baseline and ClearSpend tasks, record receipt count, task boundaries, active handling time separately from elapsed waiting, errors, correction cycles, sample size and unsuccessful runs. Synthetic operating metrics alone do not demonstrate customer savings.
5. Maintain a distinct participant roster with dates, relevant roles, consent status and observations. Several documents about one person count as one participant. Pricing follow-ups must distinguish stated interest, responses to an exact offer and an actual paid commitment.
