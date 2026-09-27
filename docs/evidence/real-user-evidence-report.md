# Real-user evidence and decision-trace report

**Assessment purpose:** demonstrate what was learned from real, relevant participants, how the evidence changed ClearSpend, and where the evidence is still incomplete. This report does not turn discovery interviews into usability tests or invent outcomes that were not observed.

## Executive conclusion

The repository contains five anonymized, consent-safe participant records across the reimbursement and finance-operations workflow:

- three directly reimbursement-relevant participants: an employee submitter, a finance reviewer, and a relocation-reimbursement stakeholder;
- two adjacent control stakeholders: a head of operations and an IT procurement leader.

Two participants provided qualitative feedback about the ClearSpend concept and workflow. Three supplied process-discovery evidence but did not perform a ClearSpend usability test. This satisfies a **five-participant qualitative research set** and a **three-participant directly reimbursement-relevant subset**. It does **not** establish five observed product users, quantified time savings, recommendation accuracy, production readiness, or willingness to pay.

## Participant relevance and provenance

| Evidence ID | Anonymized participant category | Relationship to the problem | Evidence collected | Product exposure recorded | Why relevant | Consent/privacy record |
|---|---|---|---|---|---|---|
| [`INT-01`](../interviews/INT-01-employee-submitter.md) | Frequent employee reimbursement submitter | Direct submitter | Current-workflow account and qualitative product feedback | ClearSpend workflow discussed; no timed task recorded | Experiences receipt submission, missing-evidence follow-up, and decision uncertainty | Consent to anonymized publication recorded; no identifying data retained |
| [`INT-02`](../interviews/INT-02-finance-reviewer.md) | Finance-team reviewer | Direct reviewer | Current-review account and qualitative product feedback | ClearSpend workflow discussed; no timed task recorded | Performs receipt, policy, approval-context, and exception review | Consent to anonymized publication recorded; no identifying data retained |
| [`INT-03`](../interviews/INT-03-head-of-operations.md) | Head of operations | Adjacent finance-operations stakeholder | Process discovery | None recorded | Owns budget, project-cost, approval, and reconciliation controls affected by expense evidence | Consent to anonymized publication recorded; no identifying data retained |
| [`INT-04`](../interviews/INT-04-it-head.md) | IT procurement leader | Adjacent control stakeholder | Process discovery | None recorded | Provides counterevidence about procurement, authorization, and reconciliation scope | Consent to anonymized publication recorded; no identifying data retained |
| [`INT-05`](../interviews/INT-05-relocation-stakeholder.md) | Relocation reimbursement stakeholder | Direct reimbursement stakeholder | Process discovery | None recorded | Describes capped reimbursement, invoice, proof-of-payment, vendor, and multi-role review needs | Consent to anonymized publication recorded; no identifying data retained |

Independence is contributor-reported in the canonical interview records. The public repository deliberately omits names, employers, recordings, contact information, receipts, and raw consent messages. If the assessor requests verification, the accountable research owner should show consent/provenance privately without adding personal data to the repository.

## Hypothesis → evidence → decision traces

### DT-01 — Consolidated evidence packet

- **Hypothesis:** placing receipts, extracted fields, deterministic checks, policy context, explanations, and history together will reduce fragmented review work.
- **Evidence:** `INT-01` and `INT-02` described repeated receipt handling and fragmented policy/approval context. `INT-03` and `INT-04` corroborated that evidence and approvals are distributed across operational tools.
- **Counterevidence/uncertainty:** no participant completed a timed comparison, so reduced effort and time saved remain unproven.
- **Decision:** retain one reviewer evidence packet rather than separate receipt, policy, and recommendation screens.
- **Implemented evidence:** [`apps/web/app/page.tsx`](../../apps/web/app/page.tsx) renders current receipt lines, previews, policy citations, checks, information requests, and audit status in the review flow.
- **Outcome status:** implemented direction; customer outcome unvalidated.

### DT-02 — Inline receipt preview

- **Hypothesis:** reviewers need to inspect receipts without downloading each file.
- **Evidence:** `INT-02` explicitly valued previewing evidence in the product rather than repeatedly downloading receipts.
- **Counterevidence/uncertainty:** feedback came from one finance reviewer; browser/PDF accessibility was not observed with multiple reviewers.
- **Decision:** retain an authorized modal preview and return the reviewer to the same queue context after closing it.
- **Implemented evidence:** [`apps/web/app/page.tsx`](../../apps/web/app/page.tsx) provides the eye-button preview dialog; [`services/backend/app/main.py`](../../services/backend/app/main.py) authorizes access, decrypts clean evidence, and audits `receipt.viewed`.
- **Outcome status:** implemented and automated-smoke covered; multi-user usability unvalidated.

### DT-03 — Continue the same case after missing information

- **Hypothesis:** when evidence is missing, continuing the original case is preferable to forcing a complete resubmission.
- **Evidence:** `INT-01` and `INT-02` valued appending missing evidence to the existing case while preserving original receipts and history.
- **Counterevidence/uncertainty:** the frequency of missing-information requests and reduction in resubmission effort were not measured.
- **Decision:** implement reviewer request-information and employee append/resubmit behavior with immutable receipt versions.
- **Implemented evidence:** [`apps/web/app/page.tsx`](../../apps/web/app/page.tsx) exposes the action-required panel and uploads only requested receipts; [`services/backend/app/db.py`](../../services/backend/app/db.py) retains receipt revisions; the smoke journey verifies preserved originals.
- **Outcome status:** implemented; behavioral benefit unquantified.

### DT-04 — Human authority over recommendations

- **Hypothesis:** finance users require AI and deterministic results to remain advisory, with a human owning the financial decision.
- **Evidence:** `INT-01` and `INT-02` supported human review. `INT-03`–`INT-05` described organization-specific approval and reconciliation responsibilities that cannot be safely collapsed into autonomous approval.
- **Counterevidence/uncertainty:** the research did not determine an optimal approval hierarchy or measure reviewer reliance/automation bias.
- **Decision:** deterministic checks run before bounded AI advice; only an authorized reviewer can approve, reject, or request information.
- **Implemented evidence:** [`services/backend/app/graph.py`](../../services/backend/app/graph.py) bounds AI orchestration, while reviewer decision endpoints and audit events remain in [`services/backend/app/main.py`](../../services/backend/app/main.py).
- **Outcome status:** implemented control; trust and reliance require observed testing.

### DT-05 — Do not expand the MVP into general spend management

- **Hypothesis:** adjacent finance processes could be handled by one generalized approval agent.
- **Evidence:** `INT-03` showed differing budget/project approval paths; `INT-04` required requisitions, quotations, purchase orders, delivery verification, and adjustments; `INT-05` required entitlement, approved-vendor, proof-of-payment, and multi-role controls.
- **Negative finding:** the generalized-agent hypothesis was not supported. These processes have materially different authorization objects, evidence, and accountable owners.
- **Decision:** reject procurement, budget-ledger, payment, and autonomous-approval expansion from the MVP. Keep ClearSpend bounded to receipt-first reimbursement review and accounting CSV handoff.
- **Implemented evidence:** the boundary is recorded in [`docs/decision-log.md`](../decision-log.md), [`docs/product/roadmap.md`](../product/roadmap.md), and the product narrative.
- **Outcome status:** scope reduced because of evidence.

### DT-06 — Visible policy context and auditability

- **Hypothesis:** reviewers will trust assistance more when policy reasons and evidence history are inspectable.
- **Evidence:** `INT-02` valued visible policy context and an audit trail. `INT-03`–`INT-05` reinforced the need to trace authorization, evidence, verification, and reconciliation.
- **Counterevidence/uncertainty:** no comprehension test established whether current explanations are sufficient or whether reviewers can detect an incorrect recommendation.
- **Decision:** show deterministic/AI source labels, explanations, pinned citations, receipt history, and a hash-linked audit trail.
- **Implemented evidence:** reviewer rendering is in [`apps/web/app/page.tsx`](../../apps/web/app/page.tsx); persistence and event chaining are represented in [`services/backend/app/db.py`](../../services/backend/app/db.py) and backend audit behavior.
- **Outcome status:** implemented; explanation quality needs direct evaluation.

## Negative findings and uncomfortable truths

These findings are intentionally retained rather than hidden:

1. Only two participants provided recorded ClearSpend product feedback; the other three did not test the product.
2. No baseline-versus-ClearSpend task timing has been observed, so time-saving claims remain hypotheses.
3. No participant response to the concrete ₹25,000 pilot offer is recorded, so willingness to pay is unvalidated.
4. The interviews do not establish a universal approval hierarchy. Operations, IT procurement, and relocation use different accountable roles and evidence.
5. The evidence does not prove recommendation accuracy, reduced fraud, production security, or accounting-system acceptance.
6. The IT procurement findings argue against expanding this MVP into purchase orders or asset management.
7. The relocation findings expose missing entitlement, approved-vendor, and proof-of-payment controls if that segment is pursued.

## Decisions demonstrably changed by evidence

| Evidence-driven change | Before/alternative | Result |
|---|---|---|
| Unified reviewer packet | Fragmented receipt/policy/decision surfaces | Receipt preview, policy, checks, recommendation, and history remain together |
| Same-case correction | Restart claim or overwrite evidence | Request-information → append/resubmit with immutable history |
| Human decision ownership | Autonomous AI approval | AI remains bounded advice; reviewer owns the final state |
| Bounded reimbursement scope | General finance/procurement agent | Procurement, payment, budget ledger, and enterprise approval-chain replacement rejected from MVP |
| Inspectable reasoning | Bare approve/reject score | Source-labelled checks, explanations, citations, and audit events retained |

## Rubric claim permitted by this evidence

The team may accurately say:

> We conducted five consent-safe qualitative interviews across the reimbursement and finance-operations workflow, including three directly reimbursement-relevant participants. Two participants supplied product feedback and three supplied process/counter-scope evidence. Six hypothesis-to-evidence-to-decision traces show what was kept, changed, or rejected. We report the absence of timed product observations and willingness-to-pay evidence as remaining risk.

The team must not say that five users completed the product, that time was saved, or that buyers agreed to pay unless new evidence is collected and recorded.

