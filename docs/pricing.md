# ClearSpend pricing and validation plan

**Status:** Active discovery pricing plan.

**Initial pricing hypothesis date:** 2026-09-17
**Current active discovery offer:** 2026-09-27

**Audience:** ClearSpend product, sales, and finance owners

## Current decision

ClearSpend will not publish self-serve pricing yet. The active commercial test is a
single paid design-partner pilot:

**₹25,000 INR, paid in advance and non-refundable, for a 30-calendar-day pilot.**

This replaces the earlier low-price pilot and provisional monthly-renewal hypotheses. Those older numbers were exploratory working assumptions and are not current offers.

The purpose of the current offer is to test whether an economic buyer will make a real
paid commitment for ClearSpend's narrow reimbursement-review MVP before ERP integration,
payment execution, or a broader finance-platform bundle exists.

## Why the price changed

The earlier low-price pilot was useful as a lightweight hypothesis, but it was too weak as a willingness-to-pay signal and unlikely to reflect the high-touch work required for a design-partner pilot.

The active ₹25,000 offer is intentionally framed as paid discovery and implementation,
not as mature SaaS pricing. It better matches the pilot reality:

- ClearSpend must configure the customer's reimbursement policy workflow.
- The team must support onboarding, review behavior measurement, and pilot success.
- The buyer must show budget-level commitment, not just interest in a cheap trial.
- The test must produce evidence about value, trust, and implementation friction.

Do not compare the old and new numbers as if they are two live pricing tiers. The old
numbers are superseded; the current test uses ₹25,000.

## Offer package

The paid pilot includes:

- one organization;
- up to 10 active reviewers;
- unlimited employee submitters for the pilot workflow;
- one configured reimbursement-policy workflow;
- receipt evidence capture and preview;
- employee-confirmed claim details;
- deterministic receipt and policy checks;
- bounded AI assistance for unresolved language ambiguity;
- policy citations, recommendation, decision workflow, audit history, and CSV accounting
  handoff;
- assisted setup;
- email support during the pilot; and
- one end-of-pilot results review.

The pilot excludes:

- custom ERP integrations;
- payment execution or reimbursement disbursement;
- card issuing, funds, budgets, AP, procurement, treasury, or payroll;
- SSO or custom enterprise identity work;
- live production-security commitments beyond the documented MVP scope; and
- unattended self-serve onboarding.

## Free evaluation boundary

ClearSpend may run a guided evaluation before offering the paid pilot, but it is not a
production trial and does not count as willingness-to-pay evidence.

A guided evaluation may use synthetic or customer-created de-identified claims to test
workflow fit, usability, trust, and task completion. It should be facilitated and limited
to the core workflow: submit or inspect a claim, review the evidence packet, distinguish
the AI recommendation from the human decision, handle an exception, and produce the CSV
handoff.

Free use, verbal interest, compliments, survey intent, and non-binding LOIs do not count
as demand.

## Discovery test gate

The active willingness-to-pay test is defined in
[`product/business-model-canvas.md#precommitted-discovery-tests`](product/business-model-canvas.md#precommitted-discovery-tests):

- **Test window:** 2026-11-02 to 2026-11-13
- **Target:** five qualified economic buyers
- **Offer:** ₹25,000 INR paid-pilot offer after workflow demonstration
- **Passing evidence:** at least two of five buyers make a paid commitment
- **Inconclusive:** one of five buyers commits
- **Fail:** zero of five buyers commit

A commitment means a signed paid-pilot agreement, purchase order, or payment. No free
pilot, non-binding LOI, or verbal interest counts.

## Billable-unit definition for the pilot

The pilot is a fixed-fee engagement, not metered usage. Usage should still be measured to
inform future pricing.

For internal measurement, a unique report or claim counts once when it first reaches a
human-ready review state during the pilot. The following should not create another counted
claim:

- failed or duplicate uploads;
- extraction retries;
- edits before review;
- information-request and resubmission cycles;
- assessment retries or technical fallbacks; and
- repeated downloads or exports.

The measured count must be reproducible from the audit history. Reviewer seats are an
access boundary for the pilot, not the validated long-term pricing metric.

## Future recurring pricing hypothesis

Recurring pricing is intentionally unresolved. Candidate models include:

- organization platform fee;
- per-active-reviewer fee;
- per-submitted-report fee;
- implementation or configuration services; and
- premium add-ons for audit retention, reporting, routing, or integrations.

Do not publish recurring prices until the paid pilot produces evidence about value,
usage, support burden, and buyer preference.

The pricing principle is to price against finance-review effort, audit/rework risk, and
workflow fragmentation—not payment volume. ClearSpend does not currently monetize card
spend, reimbursement payment volume, treasury yield, or interchange.

## Value hypothesis and buyer economics

The primary value hypothesis is that ClearSpend reduces avoidable finance-review effort
without increasing policy, evidence, or coding errors. Auditability, fewer follow-ups, and
more consistent decisions are secondary value hypotheses until buyers quantify them.

Use the buyer's measured inputs:

```text
monthly buyer value
= claims per month × reviewer minutes saved per claim / 60 × loaded hourly cost
+ avoided correction and follow-up cost
+ quantified audit-preparation value
```

The break-even time saving for any future recurring price is:

```text
minutes saved per claim
= price × 60 / (claims processed × loaded reviewer hourly cost)
```

Do not claim labor-cost savings unless measured saved time is demonstrably convertible
into reduced labor, contractor, overtime, or support cost.

## Seller unit economics

Record actual cost during the pilot rather than inventing a margin:

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

Calculate contribution at observed usage and at the package boundary. A design-partner
pilot may be treated as paid discovery, but support burden must remain visible.

## Evidence to record for every offer

For every paid-pilot offer, record:

- buyer and decision-maker role;
- segment fit and current reimbursement workflow;
- offered package and price;
- accepted or rejected outcome;
- payment, purchase order, or signed agreement status;
- discounts, concessions, or custom-work requests;
- stated rejection or acceptance reason;
- actual pilot usage;
- onboarding and support effort;
- measured reviewer-time and decision-quality results; and
- renewal or expansion decision.

## Rejected alternatives for now

- **Unattended free trial:** rejected because accepting it is costless, setup requires
  assistance, and the current product is not ready for unsupervised live financial data.
- **Published monthly SaaS price:** rejected until ClearSpend has evidence about measured
  value, usage, buyer preference, and cost-to-serve.
- **Per-seat-only pricing:** risky because occasional approvers, auditors, and employees
  are necessary participants; charging for every access role may suppress adoption or
  encourage shared accounts.
- **Pure per-claim pricing:** risky because it makes every marginal claim feel like a
  charge and may discourage legitimate workflow use.
- **Outcome-based pricing:** rejected until ClearSpend and the customer can independently
  recompute the outcome, observation window, and treatment of corrections and escalations.

## Data and product boundaries

The current evaluation and pilot should use synthetic or customer-created de-identified
cases unless explicit written approval and production controls are in place. Do not ingest
names, personal email addresses, employee identifiers, bank or tax details, card data, or
original receipts containing personal information unless the controls in
[`known-limitations.md`](known-limitations.md) have been addressed.

ClearSpend provides decision support and an accountant-ready CSV. It does not approve on
behalf of the reviewer, move money, prove reimbursement, or prove that an accounting
system accepted the export.

## Change-my-mind conditions

Revisit the active offer when any of the following occurs:

- at least two of five qualified buyers pay or commit at ₹25,000;
- zero of five qualified buyers commit after confirming problem and package fit;
- buyers consistently reject the offer for the same specific package gap;
- measured support or processing cost makes the pilot economically unacceptable;
- observed value is driven primarily by audit risk rather than reviewer time; or
- production readiness permits a safe unattended trial with live customer workflows.

## Evidence status

The package, price, value threshold, and future recurring model are hypotheses. The
repository currently contains engineering evidence, synthetic workflow evidence, and
limited qualitative interview evidence. It does not yet contain paid-pilot evidence,
renewal evidence, measured customer baselines, validated willingness to pay, competitive
price benchmarks, or observed unit economics. GST treatment and contractual payment terms
remain outside this artifact and require appropriate business or professional review.
