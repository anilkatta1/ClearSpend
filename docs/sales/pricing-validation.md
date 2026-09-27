# Pricing validation

**Owner:** Niraj Gupta  
**Canonical pricing plan:** [`../pricing.md`](../pricing.md)  
**Status:** package logic documented; willingness to pay not validated

## Sales offer under test

Sales will use one exact offer in every buyer conversation:

- **Price:** ₹2,499 once, paid for a 30-day design-partner pilot.
- **Organization scope:** one company and one active reimbursement policy.
- **Usage:** up to 100 unique reimbursement claims.
- **Access:** five reviewer or administrator accounts and unlimited employee submitters.
- **Included workflow:** receipt extraction and employee confirmation, deterministic receipt and policy checks, bounded AI assistance, policy citations, human approval and information requests, audit history, CSV export, assisted setup, email support, and one end-of-pilot review.
- **Overages:** none. Reaching 100 claims triggers a commercial review rather than an automatic charge or interruption.

This price is a test hypothesis, not a validated market price. The ₹25,000 test offer currently written in `docs/product/business-model-canvas.md` is not part of the Sales offer and must be synchronized before final submission.

## Countable willingness-to-pay evidence

A countable result requires:

- Participant role and purchase authority
- Exact package and exact price presented
- Accept, reject, or escalate response
- Main reason or objection
- Discount or customization requested
- Concrete next action and date
- Signed agreement, purchase order, or payment when claiming a paid commitment

Compliments, survey intent, willingness to attend a free evaluation, and non-binding interest do not count as willingness to pay.

## Offer-response log

| Offer ID | Participant ID | Purchase authority | Exact package and price | Response | Objection/reason | Concession requested | Next action | Evidence |
|---|---|---|---|---|---|---|---|---|
| — | — | — | ₹2,499 for the defined 30-day pilot | No validated response recorded | — | — | Present the exact offer to qualified buyers | — |

## Unit economics to measure

```text
contribution
= collected price
- receipt extraction and OCR cost
- AI invocation rate × AI cost per invocation
- storage, hosting, and export cost
- onboarding and support hours × loaded hourly cost
- payment fees
- expected correction or remediation cost
```

Measure expected usage and the full package allowance. Illustrative calculations are not customer or cost evidence.

## Rejected alternatives

- **Unattended free trial:** rejected while the product remains a synthetic-data MVP and policy setup needs assistance.
- **Per-seat pricing:** rejected because occasional approvers and submitters should not be discouraged from participation.
- **Pure per-claim pricing:** rejected because retries, edits, and information-request cycles should not create surprising charges.
- **Outcome pricing:** rejected until the customer and ClearSpend can independently recompute the business outcome.
