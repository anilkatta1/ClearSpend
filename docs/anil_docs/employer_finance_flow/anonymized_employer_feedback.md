# Anonymized employer/finance-stakeholder feedback

- **Recorded by:** Anil Katta
- **Interview date:** 21 September 2026
- **Participant:** one finance-team member in Anil's organization; name and organization withheld
- **Method:** informal semi-structured interview/conversation about the existing reimbursement flow followed by discussion of ClearSpend and its expected benefits
- **Interview guide:** [`interview_script.md`](interview_script.md), reconstructed from the topics Anil reports discussing
- **Format:** anonymized summary supplied by Anil, not a verbatim transcript
- **Consent/privacy:** Anil confirms that the participant consented to publication with anonymization. The consent channel (verbal or written) was not recorded in the supplied notes. No personal, client or organization-identifying information is included.

## Accuracy check

This summary was rechecked on 27 September 2026 against the account supplied by Anil. Every statement attributed to the participant maps to one of the reported feedback points: reducing repeated manual verification, avoiding receipt downloads through preview, showing policy context directly, supporting audit, retaining human review, and continuing the same workflow after requesting more evidence. Product interpretation, limitations and recommended next questions are kept in separately labeled sections.

The summary is therefore an accurate edited representation of Anil's supplied account. It is not a verbatim transcript and has not been marked as independently participant-verified.

## Feedback supplied by Anil

The stakeholder's view was that this automation could save substantial time otherwise spent manually examining receipts, checking policies and contacting different people to establish whether an expense was within an approved budget. Bringing that information together would reduce the effort required to reach an approval decision.

The stakeholder particularly valued the ability to preview receipts within the product rather than downloading every file. Displaying the relevant policy and explanation next to the receipt would also make review more efficient and reduce the need to search separate policy documents.

The stakeholder considered the product useful for audit because the evidence, recommendation, policy context and human decision can be reviewed together. They also valued the human-in-the-loop design: a reviewer can request another receipt or missing information, and the employee can continue the existing workflow rather than creating the reimbursement again from the beginning.

## Validated themes

| Theme | Evidence from this feedback | Product implication |
|---|---|---|
| Repeated manual verification | Stakeholder described manual receipt, policy and approval-context checking as time-consuming | Keep deterministic checks and a unified review packet central to the value proposition |
| Receipt usability | Stakeholder valued previewing evidence without downloading each file | Preserve inline preview and test it with reviewers across supported formats |
| Policy visibility | Stakeholder valued seeing policies directly during review | Continue showing pinned citations and explanations beside check results |
| Audit readiness | Stakeholder saw value in a combined evidence and decision record | Retain immutable receipt history, assessment attempts and audit events |
| Human authority | Stakeholder valued the reviewer's ability to ask for more evidence | Keep final decisions human-owned and make uncertainty/request states explicit |
| Workflow continuity | Stakeholder valued continuing after a request instead of restarting | Preserve append/resubmit behavior and previous evidence versions |

## Hypothesis → evidence → decision traces

### Trace E1 — unified evidence reduces reviewer effort

- **Hypothesis:** A reviewer will value one screen containing receipt evidence, policy results and approval context.
- **Evidence:** The stakeholder reported that manually checking receipts, policies and information from different people is burdensome and believed the unified automated workflow would save time.
- **Decision:** Retain the unified reviewer view as the primary workflow. Do not split receipts, policy results and explanations across separate operational tools.
- **Remaining validation:** Measure active review time and external lookups with at least three relevant reviewers; this interview supplies perceived value, not a quantified saving.

### Trace E2 — inline preview is operationally meaningful

- **Hypothesis:** Previewing receipts in the application is preferable to downloading each receipt.
- **Evidence:** The stakeholder explicitly identified in-product preview as useful.
- **Decision:** Keep modal preview in the reviewer flow and preserve authorization/audit checks on every preview.
- **Remaining validation:** Test large, rotated and multi-page receipts and measure whether reviewers still download files.

### Trace E3 — visible policy citations improve trust

- **Hypothesis:** Reviewers are more likely to trust assistance when the relevant policy is visible beside the result.
- **Evidence:** The stakeholder valued direct policy visibility rather than locating policy separately.
- **Decision:** Continue displaying deterministic/AI source labels, result status, reason and pinned policy citations. Do not present a bare approve/reject score.
- **Remaining validation:** Confirm that citations are understandable and sufficient for disputed cases.

### Trace E4 — information requests should continue the same case

- **Hypothesis:** Missing evidence should not force an employee to restart the reimbursement.
- **Evidence:** The stakeholder valued requesting another receipt and continuing the existing workflow.
- **Decision:** Preserve `INFORMATION_REQUESTED → SUBMITTED`, append/replace semantics, immutable receipt revisions and reassessment of the new revision.
- **Remaining validation:** Measure whether employees understand the difference between appending a missed receipt and replacing the complete evidence bundle.

### Trace E5 — audit history is part of the product value

- **Hypothesis:** A connected record of evidence, policy checks and human decisions matters to employer-side stakeholders.
- **Evidence:** The stakeholder identified auditing as a useful outcome.
- **Decision:** Treat receipt versions, assessment attempts, policy citations, override reasons and hash-linked audit events as product features, not only backend logs.
- **Remaining validation:** Ask an auditor to reconstruct a completed decision without assistance and document any missing evidence.

## Team interpretation — not attributed to the participant

This feedback supports the product direction but does not prove a specific time saving, willingness to pay or production readiness. It confirms several features that already existed; the team should distinguish confirmation from evidence that directly caused a new change.

The next interviews should test potential objections as well as benefits:

- whether a single-reviewer MVP fits the organization's actual approval hierarchy;
- how approved-budget evidence should enter the system;
- when a reviewer distrusts OCR or a recommendation;
- which policy exceptions require escalation;
- what auditors need to export or retain;
- what price is acceptable and who owns the purchase decision.

## Evidence still needed

Consent for anonymized publication is confirmed. If possible, the participant should also confirm that this edited summary accurately represents the conversation; this is additional quality assurance rather than a prerequisite to record the consent already provided. The team still needs additional relevant users/stakeholders to meet the required 3–5-user evidence threshold.
