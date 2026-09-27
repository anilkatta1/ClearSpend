# Customer validation evidence register

**Purpose:** track the three separate requirements without converting qualitative opinions into quantified outcomes:

1. evidence from 3–5 independent relevant users;
2. quantified baseline and time-saved evidence;
3. willingness-to-pay evidence.

## 1. Independent relevant-user threshold

| Record | Participant category | Reimbursement relevance | Evidence available | Counts toward qualitative threshold | Counts as observed product-use evidence |
|---|---|---|---|---|---|
| [`INT-01`](../interviews/INT-01-employee-submitter.md) | Frequent employee submitter | Direct | Consent-safe workflow/product-feedback summary | Yes | No measured task observation recorded |
| [`INT-02`](../interviews/INT-02-finance-reviewer.md) | Finance reviewer | Direct | Consent-safe workflow/product-feedback summary | Yes | No measured task observation recorded |
| [`INT-03`](../interviews/INT-03-head-of-operations.md) | Head of operations | Adjacent process discovery | Consent-safe process summary | Context only | No |
| [`INT-04`](../interviews/INT-04-it-head.md) | IT head | Adjacent procure-to-pay discovery | Consent-safe process summary | Context only | No |
| [`INT-05`](../interviews/INT-05-relocation-stakeholder.md) | Relocation reimbursement stakeholder | Direct | Consent-safe process/product-feedback summary | Yes | No measured task observation recorded |

**Current conclusion:** three independent reimbursement-relevant qualitative records exist. The stronger requirement—observing representative users completing ClearSpend tasks and recording outcomes—remains unmet. The evidence must not be described as proof of time saved, recommendation accuracy, willingness to pay, or production readiness.

## 2. Quantified baseline and time-saved evidence

### Measurement protocol

Use the same synthetic claim scenario for the current process and ClearSpend. For each participant:

1. Obtain consent for anonymized observation and timing.
2. Define the task and start/stop rules before timing.
3. Record active task time, excluding interruptions unrelated to the task.
4. Record receipt downloads, policy lookups, external messages/calls, errors and requested-information events.
5. Run the corresponding ClearSpend task without coaching beyond the standard demo instructions.
6. Record whether the participant reached the correct human decision and could explain it from the evidence.
7. Preserve negative findings and failed tasks.

### Results table

Do not fill this table from memory or expectation. Enter values only after an observed session.

| Observation ID | Participant role | Consent recorded | Scenario | Current-process active minutes | ClearSpend active minutes | Minutes saved | Relative reduction | External lookups before/after | Decision correct/explainable | Evidence reference |
|---|---|---|---|---:|---:|---:|---:|---|---|---|
| Pending | — | — | — | — | — | — | — | — | — | — |

Calculations:

```text
minutes saved = current-process minutes - ClearSpend minutes
relative reduction = minutes saved / current-process minutes
```

Report the median across completed relevant-user observations. Do not extrapolate annual savings until observed frequency and loaded labor cost are independently documented.

## 3. Willingness-to-pay evidence

The current ₹25,000 design-partner pilot is an offer hypothesis, not validated willingness to pay.

### Evidence hierarchy

From strongest to weakest:

1. paid pilot or signed purchase order;
2. signed letter of intent with price and conditions;
3. written acceptance subject to named procurement/security conditions;
4. explicit interview response to the concrete ₹25,000 offer;
5. general statement that the product is useful—this does **not** establish willingness to pay.

### Offer-response register

| Evidence ID | Buyer role/category | Offer presented | Exact response category | Conditions/objections | Amount accepted/countered | Evidence reference | Decision impact |
|---|---|---|---|---|---:|---|---|
| Pending | — | ₹25,000 design-partner pilot | Not yet tested | — | — | — | Pricing remains a hypothesis |

Allowed response categories are `ACCEPTED`, `CONDITIONAL`, `COUNTERED`, `DECLINED`, and `NO_DECISION`. Preserve the participant's meaning without including identifying or commercially sensitive information.

## Completion criteria

This evidence area is complete only when:

- 3–5 independent relevant users have consent-safe records;
- representative employee and finance-reviewer product tasks have been directly observed;
- baseline and ClearSpend timings use a documented comparable protocol;
- negative findings and errors are retained;
- a concrete priced offer has received explicit buyer responses;
- resulting product, roadmap or pricing decisions cite the evidence IDs above.

