# Anil Katta — employee experience and product feedback

- **Contributor:** Anil Katta
- **Perspective:** employee familiar with the reimbursement process and engineer/architect responsible for ClearSpend
- **Evidence type:** first-person experience supplied by Anil; edited for clarity
- **Privacy:** organization and colleagues are not identified

## My experience with the current process

In my organization, an employee reimbursement has historically passed through several people before it can be approved. Although each approver has a legitimate responsibility, much of the work is repeated at every step. People download the same receipts, inspect merchant, date and amount details, compare the claim with the permitted budget, contact the people who originally approved the activity or budget, and manually read the relevant reimbursement policies.

The work is spread across receipts, messages, policy documents and prior approvals. A reviewer may not know whether an earlier person already checked a particular fact, so the safe response is to check it again. This creates delay for the employee and repetitive administrative work for finance and managers. It also makes the final rationale difficult to reconstruct later because parts of the explanation can remain in email or chat instead of one auditable record.

## My experience of the ClearSpend flow

ClearSpend brings the evidence and policy evaluation into one workflow. An employee can upload one or more receipts for the same expense category, verify the extracted merchant, date and amount, and submit one report. The system checks each receipt against the employee-confirmed line, evaluates the report against the pinned policy version, and presents a recommendation with reasons and policy citations.

This does not remove human accountability. The reviewer still decides whether to approve, reject or request more information. The value is that the reviewer receives a prepared evidence packet instead of reconstructing it manually. When more evidence is requested, the employee can append the missing receipt or information and continue the existing case. The original receipts, replacement history and decisions remain available for audit.

From my perspective, the most useful improvements are:

- fewer repeated downloads and manual comparisons;
- a single place to preview all submitted receipts;
- merchant, date and amount checks for each receipt line;
- visible policy rules and explanations alongside the recommendation;
- one report for multiple same-category receipts, such as a business trip;
- human review for ambiguous or failed checks;
- continuation after an information request instead of restarting the claim;
- an audit history that connects evidence, recommendation and final human decision.

## Trust and safety observations

The product is more credible because objective limits and prohibitions are evaluated deterministically rather than delegated to an LLM. Receipt uploads are quarantined, malware-scanned and structurally checked before they can be used. AI is optional and limited to purpose plausibility; it cannot approve an expense, alter policy, export accounting data or move money.

The product must present this boundary clearly. A recommendation is decision support, not an approval. Reviewers should be able to see why a check passed, failed or remained unknown, and auditors should be able to identify which policy and receipt versions were used.

## Important limitations

This account is my own perspective and is not independent customer validation. The current MVP has one final reviewer decision rather than an arbitrary configurable chain of approvers. It centralizes the evidence that multiple stakeholders can use, but it should not be described as having replaced every organization's approval hierarchy.

Before production use, we would also need production identity and sessions, managed encryption keys, retention/deletion controls, validated OCR accuracy on real consented samples, and integration with the organization's source of budget approval or accounting system.

## Suggested success measures

The perceived time saving should be validated with measured evidence:

- median active reviewer time per report before and after ClearSpend;
- number of receipt downloads or external lookups per report;
- percentage of reports requiring additional information;
- reviewer agreement and override rate against system recommendations;
- time from initial submission to final decision;
- number of cases for which an auditor can reconstruct the decision without contacting another person.
