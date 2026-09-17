# ClearSpend pricing and validation plan

**Status:** Working hypothesis, not validated pricing

**Decision date:** 2026-09-17

**Audience:** ClearSpend product, sales, and finance owners

## Decision

ClearSpend will use a two-stage commercial path:

1. A free, guided evaluation tests workflow fit, usability, and trust.

2. A paid design-partner pilot tests willingness to pay and measurable value.

ClearSpend will not offer an unattended free trial while the product remains a

synthetic-data MVP. It will not publish a larger tier or automatic overage price until

pilot usage and seller costs are measured.

## Free guided evaluation

The evaluation is a 60-minute facilitated session using three to five synthetic or

customer-created de-identified claims. It is not a production trial and is not evidence

of willingness to pay.

The participant completes the core workflow: submit a claim, inspect the evidence and

policy citations, distinguish the recommendation from the human decision, handle one

exception, and produce the accounting CSV.

The evaluation passes when:

- at least four of five qualified participants complete the core workflow without the

facilitator taking control;

- at least four of five correctly explain that the AI recommendation is advisory and a

human owns the decision; and

- observed blockers, requests, and contradictory feedback are retained in the research

record rather than averaged away.

Passing this gate supports offering the paid pilot. It does not validate the price.

## Paid design-partner pilot

**Price:** ₹2,499 once for 30 days.

The package includes:

- one company and one active policy;

- up to 100 unique reimbursement claims;

- five reviewer or administrator accounts;

- unlimited employee submitters;

- receipt extraction and employee confirmation;

- deterministic receipt and policy checks;

- bounded AI assistance for unresolved language ambiguity;

- policy citations, approval and information-request workflow, audit history, and CSV

export;

- assisted setup, email support, and one end-of-pilot results review.

There are no automatic overages. Reaching 100 claims triggers a commercial review, not

an automatic charge or service interruption.

## Provisional conversion offer

If the pilot passes its value and safety gates, the working renewal hypothesis is

**₹2,999 per company per month for up to 100 unique claims**. It carries the same account

limits and product boundaries as the pilot.

This is not a published or validated market price. A higher-volume package remains

unknown until customers exceed the allowance and ClearSpend measures marginal cost,

support demand, and value at that volume.

## Billable-unit definition

A unique claim counts once when it first reaches a human-ready review state during the

billing period. The following do not create another billable claim:

- failed or duplicate uploads;

- extraction retries;

- edits before review;

- information-request and resubmission cycles;

- assessment retries or technical fallbacks; and

- repeated downloads or exports.

The billed count must be reproducible from the audit history. Reviewer seats are an

access boundary, not the primary pricing metric.

## Value hypothesis and buyer economics

The primary value hypothesis is that ClearSpend reduces finance-review effort per

accountant-ready claim without increasing policy errors. Auditability, fewer follow-ups,

and more consistent decisions are secondary value hypotheses until buyers quantify them.

Use the buyer's measured inputs:

```text

monthly buyer value

= claims per month × reviewer minutes saved per claim / 60 × loaded hourly cost

+ avoided correction and follow-up cost

+ quantified audit-preparation value

```

The break-even time saving is:

```text

minutes saved per claim

= price × 60 / (claims processed × loaded reviewer hourly cost)

```

Illustration only: at 100 claims and a loaded reviewer cost of ₹600/hour, the ₹2,499

pilot breaks even at about 2.5 minutes saved per claim; the ₹2,999 renewal breaks even at

about 3 minutes. The hourly rate, baseline time, and avoided-cost terms must be replaced

with customer evidence.

## Seller unit economics

Record actual cost rather than inventing a margin:

```text

contribution

= collected price

- receipt extraction cost

- AI invocation rate × AI cost per invocation

- storage, hosting, and export cost

- onboarding and support hours × loaded hourly cost

- payment fees

- expected correction or remediation cost

```

Calculate contribution at expected usage and at the full 100-claim allowance. A pilot

may be treated as paid discovery, but its support burden must remain visible. Offer the

renewal only when recurring costs are covered and the team has explicitly accepted the

resulting margin and onboarding-payback period.

## Pilot evidence and decision gates

Before the pilot, record the named budget decider, the current workflow, a comparable

baseline, the exact offer, and the default action if the pilot fails.

### Value and safety gates

- **Pass:** median active reviewer time per completed claim falls by at least 30% against

a comparable baseline; no material policy error is attributable to ClearSpend; every

final decision and accounting code remains human-confirmed; and billed usage is

independently reproducible.

- **Narrow:** reviewer time falls by 15–29%, or the target is reached only with material

unpriced support. Improve the product or narrow the segment before making a renewal

claim.

- **Stop:** a sensitive-data boundary is breached, tenant isolation fails, the system

makes a final financial decision, or a material policy error is concealed or left

unresolved.

Pilot results based on synthetic or simulated claims must be labeled simulation evidence,

not proof of production savings.

### Willingness-to-pay gates

- One buyer paying ₹2,499 without an undisclosed concession supports running that pilot;

it does not establish a market price.

- Three of twelve qualified buyers paying the same price supports retaining ₹2,499 as

the working pilot price.

- One or two payments support further pilot learning but not repeatable pricing.

- Zero payments requires diagnosing product trust, package fit, purchasing friction, and

price separately before changing the number.

- Renewal at ₹2,999 is stronger evidence than initial pilot payment.

For every offer, record the decider, offered package, accepted or rejected price,

discounts or custom work, stated reason, actual usage, and renewal decision. Compliments,

survey intent, and acceptance of the free evaluation are not willingness-to-pay evidence.

## Rejected alternatives

- **Unattended free trial:** rejected for now because accepting it is costless, policy

setup requires assistance, and the current product is not ready for live customer

financial data. The guided evaluation serves the usability-learning purpose.

- **Per-seat pricing:** rejected because occasional approvers and employees are necessary

participants; charging for access could suppress adoption or encourage shared accounts.

- **Pure per-claim pricing:** rejected because it makes every marginal claim feel like a

charge and creates pressure to avoid or split legitimate work. Included usage keeps

spend predictable while bounding workload.

- **Outcome-based pricing:** rejected until ClearSpend and the customer can agree on and

independently recompute a real business outcome, its observation window, and treatment

of corrections and escalations.

## Data and product boundaries

The current evaluation and pilot use synthetic or customer-created de-identified cases.

Do not ingest names, personal email addresses, employee identifiers, bank or tax details,

card data, or original receipts containing personal information. Live customer financial

data requires the production controls listed in `known-limitations.md`.

ClearSpend provides decision support and an accountant-ready CSV. It does not approve on

behalf of the reviewer, move money, prove reimbursement, or prove that an accounting

system accepted the export.

## Change-my-mind conditions

Revisit this decision when any of the following occurs:

- three qualified buyers reject the package specifically because ₹2,499 exceeds perceived

value after confirming the problem and package fit;

- three customers request more than 100 monthly claims;

- measured support or processing cost makes either offer economically unacceptable;

- observed value is driven primarily by audit risk rather than reviewer time; or

- production readiness permits a safe unattended trial with live customer workflows.

## Evidence status

The package, price, allowance, value threshold, and conversion offer are hypotheses. The

repository currently contains engineering and synthetic workflow evidence, but no paid

invoice, renewal, measured customer baseline, validated willingness to pay, competitive

price benchmark, or observed unit economics. GST treatment and contractual payment terms

also remain outside this artifact and require appropriate business or professional review.