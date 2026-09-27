# Research insights: reimbursement evidence and review

**Sources:** [I-01–I-05](README.md) in [`interview-summaries.md`](interview-summaries.md).  
**Consent:** anonymized sharing consent received 18 September.

## What we heard

| Finding | Supporting evidence | Confidence / boundary |
|---|---|---|
| Reviewers reconstruct the same evidence repeatedly when receipts, budget context, prior decisions, and policy live in separate places. | I-01; corroborating process patterns in I-02 and I-04 | Qualitative; no time measurement |
| A reviewer benefits from viewing receipts, policy context, recommendation, and decision history together. | I-01 | Direct product feedback from one finance reviewer |
| Human approval remains necessary for ambiguous evidence and organizational accountability. | I-01; approval patterns in I-02–I-04 | Strong design constraint, not proof of preferred approval-chain configuration |
| Missing evidence should continue an existing case rather than force a restart. | I-01 | Direct product feedback from one finance reviewer |
| Authorization, verification, and reconciliation must remain traceable. | I-02–I-04 | Adjacent process discovery; ClearSpend currently covers only the reimbursement-review portion |

## Hypothesis → evidence → decision

| ID | Hypothesis | Evidence | Decision |
|---|---|---|---|
| D-01 | A unified evidence packet reduces avoidable reviewer effort. | I-01 described repeated receipt, policy, and approval-context checking; I-02/I-04 show evidence and approvals are distributed across tools. | Keep receipt previews, deterministic checks, policy citations, recommendation, and decision history in the reviewer flow. |
| D-02 | Inline receipt preview is operationally meaningful. | I-01 explicitly preferred in-product preview to repeated downloads. | Retain inline/modal preview with authorization and audit checks. |
| D-03 | Visible policy context improves trust in assistance. | I-01 valued direct policy visibility; I-02/I-04 depend on budget/policy controls. | Show pinned policy citations, reasons, and check status; do not present a bare approve/reject score. |
| D-04 | Evidence gaps should be resolved in the same case. | I-01 valued requesting and appending missing evidence without restarting. | Preserve information-request → resubmission and immutable receipt revision behavior. |
| D-05 | The MVP must not claim to replace enterprise approval, procurement, budget, or payment systems. | I-02–I-04 describe organization-specific controls beyond reimbursement review. | Keep the scope to human-reviewed reimbursement evidence and accounting CSV handoff; label integrations and multi-stage approvals as future validation. |

## What this does *not* establish

- It does not establish a quantified time saving, willingness to pay, production readiness, or an optimal approval hierarchy.
- I-02–I-04 are workflow-discovery interviews, not ClearSpend product tests.
- I-05 is internal context and does not count as an independent user.
- The assignment still needs additional consent-safe observations to meet its 3–5 relevant-user threshold, including negative findings and adoption objections.

## Next research

1. Test active reviewer time, external lookups/downloads, information-request rate, and time to final decision with at least three relevant independent users.
2. Ask finance, budget owners, and auditors about exceptions, approval-chain configuration, budget-system evidence, retention/export needs, security concerns, and willingness to pay.
3. Record each result with an evidence ID, anonymized role, consent status, contradiction or objection, and the resulting keep/change/reject decision.
