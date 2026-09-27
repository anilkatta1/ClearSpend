# Direct product-observation kit

**Use:** convert the existing qualitative research into honest behavioral evidence. Complete one copy of the session record for each participant. Blank forms and planned sessions are not evidence.

## Minimum sample

Run 3–5 independent sessions, including at least:

- one frequent employee reimbursement submitter;
- two finance reviewers or approvers;
- optionally one auditor/control owner and one reimbursement program owner.

Do not use project-team members as the primary validation sample. Use synthetic receipts only.

## Consent script

> We are evaluating ClearSpend, not you. The session uses synthetic reimbursement data. We would like to record anonymized observations, task timing, errors, and your feedback for an academic assignment. We will not publish your name, employer, contact details, screen recording, or confidential process data. You may stop at any time or decline any question. Do you consent to participate and to anonymized reporting?

Record `YES` or `NO`, date, facilitator, and the private location of the consent evidence. Do not put personal identifiers or raw consent messages in the public repository.

## Comparable task scenarios

### Employee task

1. Submit the supplied synthetic hotel and transit receipts as one business-trip reimbursement.
2. Correct any extracted merchant/date/amount field that is wrong.
3. Respond to a request for one missing receipt without resubmitting the original receipts.
4. Explain the current state and next accountable role.

### Finance-reviewer task

1. Find the assigned reimbursement report.
2. Inspect each receipt and identify the merchant/date/amount match status.
3. Find the relevant policy and explain the recommendation.
4. Request missing information, or make a human decision when evidence is sufficient.
5. Explain why the recommendation is advisory rather than the final decision.

### Auditor/control task

1. Locate a report and its receipt revision history.
2. Identify who submitted, requested information, resubmitted, and decided.
3. Verify the audit-chain status and locate the accounting handoff state.
4. Identify one control or evidence item that remains missing.

## Observation rules

- Start timing when the participant receives the task; stop when they state completion.
- Record active handling time separately from waiting/system time.
- Do not coach unless the participant is irrecoverably blocked; record every intervention.
- Record incorrect decisions, abandoned tasks, confusing labels, security concerns, and mistrust.
- Ask the participant to think aloud, but do not lead them toward a feature.
- Use the same synthetic scenario for baseline and ClearSpend comparison.
- Preserve unsuccessful sessions in the result set.

## Session record

Copy this section into `OBS-0X-<role>.md` only after a real session.

```markdown
# OBS-0X — <anonymized role>

- Session date:
- Facilitator:
- Participant category:
- Reimbursement frequency/responsibility:
- Relationship to project team, if any:
- Consent to participate: YES/NO
- Consent to anonymized publication: YES/NO
- Private consent evidence reference:
- Scenario:
- Product/commit tested:

## Measures

| Measure | Current process | ClearSpend |
|---|---:|---:|
| Active handling time | | |
| Waiting/system time | | |
| Receipt downloads | | |
| Policy lookups | | |
| External messages/calls | | |
| Errors or wrong turns | | |
| Facilitator interventions | | |
| Task completed | YES/NO | YES/NO |
| Decision correct and explainable | YES/NO/N/A | YES/NO/N/A |

## Observed behavior

- What the participant did without prompting:
- Where the participant hesitated:
- Errors or unsuccessful steps:
- Evidence they relied on:
- Evidence they ignored or distrusted:

## Feedback

- Most useful aspect:
- Most confusing or risky aspect:
- Missing control/information:
- Would they use it in their role? Why/why not?
- Concrete objection:

## Trace

- Hypothesis tested:
- Evidence observed:
- Negative/contradictory evidence:
- Decision: KEEP / CHANGE / REJECT / INVESTIGATE
- Owner and target date:
- Product/document changed:
```

## Debrief questions

Ask after the task, not before:

1. What decision did you believe the system was asking you to make?
2. Which evidence did you trust, and which evidence did you verify independently?
3. What, if anything, made the recommendation difficult to understand?
4. What could cause an unsafe approval or rejection?
5. When would you request more information rather than decide?
6. What would prevent you or your organization from using this workflow?
7. Which existing tool or person would still be required?
8. What should ClearSpend explicitly refuse to do?

## Synthesis rule

After all sessions, report median active time and the count of completed tasks, errors, external lookups, interventions, and correct/explainable decisions. Report ranges and every failed session. With a sample of 3–5, describe results as directional, not statistically representative.

