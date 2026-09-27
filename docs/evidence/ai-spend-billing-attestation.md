# AI/API/tool spend — billing attestation register

**Purpose:** provide an assessor-readable record that separates billed values, owner-reported values, reconstructed estimates, and missing declarations. An estimate must never be presented as an invoice or billing-owner confirmation.

## Current spend register

| Owner/runtime | Provider/tool | Period | Amount (USD) | Evidence class | Source | Billing-owner confirmation |
|---|---|---|---:|---|---|---|
| ClearSpend product runtime | Configured fake AI provider | Verified demo | 0.0000 | Verified runtime fact | `AI_PROVIDER=fake`; no external model call in verified demo | Not applicable |
| Diya Mondal | OpenAI Codex | Usage summary recorded 27 Sep 2026 | 16.7903 | Contributor-reported account usage | [`diya-ai-spend-log.md`](diya-ai-spend-log.md) | Contributor report present; invoice/account-owner attestation not attached |
| Anil Katta | OpenAI Codex | ClearSpend-scoped local sessions through 27 Sep 2026 | 186.9646 | Reconstructed inclusive estimate | [`anil-ai-spend-log.md`](anil-ai-spend-log.md) | Pending; do not describe as billed spend |
| Prashant Chouksey | OpenAI Codex, Gemini and Grok (versions partially specified) | Assignment period | — | Contributor-declared use; hypothetical usage estimate only | [`prashant-ai-spend-log.md`](prashant-ai-spend-log.md) | Billed amount pending |
| Niraj Gupta | Undeclared | Assignment period | — | Missing declaration | None | Pending |
| **Current documented subtotal** |  |  | **203.7549** | One reported amount plus one estimate; excludes Prashant's and Niraj's unknown spend and is not a final billed team total | Linked owner logs | Incomplete |

## What qualifies as real billing evidence

At least one of the following should support each non-zero amount:

- provider billing/usage export showing the account, period, currency and amount;
- invoice line or account statement with unrelated sensitive fields redacted;
- written confirmation from the account/billing owner that states the amount and period;
- for subscription-included access, confirmation of the subscription charge and the documented allocation method used for this project.

Screenshots or exports may be retained outside the public repository if they expose account identifiers. The repository should contain a redacted evidence reference or an owner attestation, not credentials or complete invoices.

## Billing-owner attestation template

Copy one block per contributor/tool and complete only from the billing source:

```text
Contributor:
Provider/tool:
Billing account owner or authorized verifier:
Covered period:
Currency:
Provider-reported usage cost:
Subscription cost allocated to this task, if applicable:
Allocation method, if applicable:
Evidence reference (redacted screenshot/export/invoice ID):
Confirmed on:
Confirmed by:
Notes/exclusions:
```

## Team-total rule

The final disclosed team total is:

```text
verified product runtime API spend
+ each contributor's provider-reported or billing-owner-confirmed development spend
+ any explicitly allocated subscription/tool charge
= final team AI/API/tool spend
```

Unknown contributor usage must remain `pending`; it must not be silently converted to zero. Anil's reconstructed estimate may be used as a clearly labeled fallback if no billing export exists, but it cannot be relabeled as real spend.
