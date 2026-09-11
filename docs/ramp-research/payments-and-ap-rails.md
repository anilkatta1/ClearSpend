# 05 — Payments, AP Rails, and Reimbursements

Card spend is money moving *toward* you from merchants. Everything in this file is money moving *out*, which is a different risk profile, a different regulatory posture, and a different failure model.

## Bill Pay

### The object design

Ramp's central structural choice, published verbatim: **"Payments are nested — there are no dedicated payment endpoints."** The payment shape goes in the same `POST /bills` request and comes back as part of the bill object on `GET /bills`.

`[inferred]` This is deliberate and correct. A payment without an authorizing invoice is an unexplained money movement — exactly the thing an AP system exists to prevent. By making payment a sub-resource of the bill, the API makes "pay someone with no invoice" structurally impossible rather than merely discouraged. Copy this. It costs you API elegance and buys you a class of fraud you cannot commit.

The bill carries: vendor, amount, due date, line items, and nested payment details.

### Status machine

```

DRAFT ──► PENDING APPROVAL ──► APPROVED ──► PAID

```

| State | Meaning |

|---|---|

| `DRAFT` | Invoice uploaded, OCR extracts details |

| `PENDING APPROVAL` | Awaiting approver sign-off |

| `APPROVED` | Ready for payment, per configured approval policy |

| `PAID` | Payment processed |

Two published constraints that reveal the security model:

- **Bills created via API are automatically approved and enter at `APPROVED`.** The API caller is trusted as the approver.

- **Draft bills can be created and updated via API but can only be approved in the dashboard.** "Bill approvals can't be triggered or managed via API."

`[inferred]` Read those two together and the logic is: an API integration that creates a complete bill is asserting it already ran approval upstream (in an ERP or procurement system). But a draft bill — one a human is meant to review — cannot be waved through by a token. That closes the attack where a stolen API key creates a draft to an attacker-controlled vendor and immediately approves it. Preserve this asymmetry.

### Payment rails

Ramp's published rail table:

| Rail | What it is | Timing |

|---|---|---|

| **Card** | Pay by Ramp card, existing or single-use virtual. Earns cashback. | Real-time |

| **ACH** | Bank transfer via verified vendor bank account | 2–3 business days |

| **Same-day ACH** | — | Same day, $10 flat fee |

| **Check** | Mailed check to vendor's address on file | 5–7 business days |

| **Wire** | Same-day domestic wire | Same day |

| **SWIFT** | International wire | Varies. $20 flat fee for USD wires, 1–5 days |

| **Stablecoin** | Payout to vendor's crypto wallet, settled on-chain | Minutes |

Each rail "carries its own shape on `POST /bills`" — a discriminated union on payment method, not one generic payment object with nullable fields. Cross-border coverage spans 190+ countries.

Published limitations: update support is limited once a payment is created, and **batch payments — one payment across multiple bills — are not supported.**

`[inferred]` The batch-payment gap is notable because vendors want it (one consolidated ACH for twelve invoices) and it is the kind of thing an incumbent like BILL supports. Its absence is probably a reconciliation decision: a single payment against N bills makes the bill-to-payment relationship many-to-many, which complicates the two-phase GL sync described in `06`. That is a real tradeoff, not an oversight — but it is a genuine gap you could exploit competitively if you solve the reconciliation properly up front.

### Why "pay by card" is the most important rail

It looks like the least interesting one. It is the most important, because it is the only outbound rail that **earns** rather than costs. Every dollar of AP you can push onto a virtual card generates interchange. This is precisely the take-rate defense described in `01` — vendor payments migrating to ACH is what compresses the blended rate, so converting AP volume to card volume is a direct revenue lever.

`[recommendation]` Build card-based AP first, before ACH. It is easier (you already have issuing), it monetizes, and it does not require money transmission licensing in the same way. Then add ACH as table stakes.

### Vendor model

A vendor is the bill-pay payee, carrying contacts (email, phone, address) and bank accounts (for ACH, wire, check, or stablecoin).

Key fields:

| Field | Purpose |

|---|---|

| `vendor_contact_id` | Default contact for payments |

| `vendor_account_id` | Default bank account for payments |

| `accounting_vendor_remote_id` | Links vendor to the ERP coding value at GL export |

Endpoints: `GET /vendors`, `GET /vendors/{id}`, `GET /vendors/{id}/contacts`, `GET /vendors/{id}/accounts`, `PATCH /vendors/{vendor_id}`.

Note what is missing: **no `POST /vendors`, and no vendor bank account creation via API.** Vendors are read-and-update only through the API. Entity bank accounts are explicitly "not manageable via API"; only vendor bank accounts are, and even then not via creation.

`[inferred]` Same reasoning as bill approval. **Adding a bank account is the single highest-value target in an AP system.** Business email compromise attacks work by changing a legitimate vendor's bank details, not by creating fake invoices. Ramp keeps that mutation off the API surface entirely and behind human verification in the UI. This is one of the most important design decisions in the whole platform and it is invisible unless you go looking for the missing endpoint.

`[recommendation]` Whatever else you compromise on, make bank-account changes require out-of-band verification: micro-deposit or open-banking validation, plus notification to a second admin, plus a cooling-off period before the new account can receive its first payment. And never expose the mutation to an API token.

### Required UUID chain for creating a bill

Published source-to-field mapping, which doubles as the reference-integrity requirement:

| Source endpoint | Response field | Request field |

|---|---|---|

| `GET /entities` | `id` | `entity_id` |

| `GET /entities` | `bank_accounts[].id` where `usage_type = BILL_PAY_BANK_ACCOUNT` | `source_bank_account_id` |

| `GET /vendors` | `vendor_id` | — |

| `GET /vendors/{id}/contacts` | — | `vendor_contact_id` |

| `GET /vendors/{id}/accounts` | `id` (ACH, wire, SWIFT, stablecoin) | `vendor_account_id` |

Note `usage_type = BILL_PAY_BANK_ACCOUNT` — bank accounts are typed by purpose. An account approved for receiving customer repayments is not automatically approved for sending vendor payments. `[recommendation]` Adopt this. Typed account usage prevents an entire class of "wrong account funded the wrong thing" errors.

### Other published constraints

- OCR upload for draft bills is **not** supported via API. Invoice **images** cannot be attached via API; PDFs work.

- Bills cannot be synced via API with Universal CSV — dashboard export only.

- AI agents can search and read bills via MCP; bill approvals are on the roadmap, not shipped.

### Ramp Flex

Deferred bill payment at 30/60/90 days, launched August 2022. Structurally: Ramp pays the vendor now and collects from the customer later.

This is a **separate credit product with a separate exposure** from the charge card, and it needs its own underwriting, its own limit, and its own loss reserve. Do not fold it into the card line. `[recommendation]` Defer this entirely until the card business is stable. It is a lending business wearing an AP feature's clothing.

## Reimbursements

### Entry paths

Three published: from the app, from a receipt upload where OCR drafts the reimbursement, and from a mileage post.

Endpoints of note:

- `POST /reimbursements/mileage` — dedicated mileage creation

- `POST /reimbursements/submit-receipt` — **drafts via OCR when no `reimbursement_id` is supplied**, otherwise attaches to an existing reimbursement

That second endpoint is an elegant piece of API design: one endpoint, two behaviors, keyed on presence of an ID. The employee photographs a receipt and the system creates the whole expense from it. Receipt-first, not form-first.

### Lifecycle

```

DRAFT → PENDING → APPROVED → REIMBURSED

```

Edge states: `REJECTED`, `CANCELED`, `FAILED_REIMBURSEMENT`, plus payment-specific `AWAITING_PAYMENT`, `PROCESSING`, `REIMBURSED_VIA_PUSH`.

`FAILED_REIMBURSEMENT` as a first-class state matters — payouts to employee bank accounts fail (closed account, wrong routing number) and the expense must return to an actionable state rather than disappearing.

`REIMBURSED_VIA_PUSH` `[inferred]` indicates push-to-card or instant payout as an alternative to ACH.

### Direction

`BUSINESS_TO_USER` (default) and `USER_TO_BUSINESS`. The reverse direction covers amounts an employee owes the business back — a personal charge on a corporate card, or an unreturned advance. Modeling both directions on one object rather than building a separate "employee repayment" feature is the right call; it is the same approval, the same coding, the same GL treatment with signs flipped.

### Policy gating

Reimbursements are gated by **funds**, the same primitive that backs cards: "funds gate which categories and amounts are reimbursable when no card is in play." A fund with no card attached is reimbursement-only.

This is the strongest argument for the fund-centric model. One policy object governs both pre-spend (card authorization) and post-spend (reimbursement eligibility). If you model card limits and reimbursement policy separately, they will drift, and your customer will discover that the thing their card blocked can be reimbursed instead.

### Currency

Covered in detail in `02-domain-model.md`. The short version: four distinct amounts (line item original, original total, business paid, payee received), and `line_items[].converted_amount` is explicitly not usable for reimbursement line items.

## Transfers, cashback, statements

Lighter-documented but present in the model:

- **Transfers** (`transfers:read`) — internal money movement between accounts. Auto-eligible for GL sync.

- **Cashbacks** (`cashbacks:read`) — rewards accrual. Also auto-eligible for GL sync. Needs a liability account and an accrual/redemption model.

- **Statements** (`statements:read`) — cycle statements for the charge card.

- **Banking transactions** — `GET /developer/v1/banking/syncable-transactions` returns banking transactions available to sync to an accounting provider.

Both transfers and cashbacks being **automatically** sync-ready (versus transactions and reimbursements, which require a user to mark ready) is a small but telling detail: system-originated money movement needs no human coding decision, so it flows straight to the GL.

## Money movement architecture

`[recommendation]` — design guidance for your build.

### Every outbound payment is a saga

An ACH debit or credit is not a request-response call. It is a multi-day process with asynchronous failure arriving up to 60 days later (unauthorized-debit returns). Model it as a durable workflow — this is precisely what Temporal is for, and Ramp runs Temporal.

```

initiate → submitted → in_transit → settled

│ │

│ └──► returned (R01 NSF, R02 closed, R03 no account,

│ R29 unauthorized corporate, ...)

└──► rejected (pre-submission validation failure)

```

Requirements:

- **Idempotency key on every initiation.** Generated by you, stored before the call, checked on retry. A double-sent wire is not recoverable by an engineer.

- **Return handling is a first-class path, not an error branch.** Returns arrive days later, must reverse the ledger entry, must notify, and must feed the return-probability model.

- **Positive pay / dual control on check.** Checks are the most fraud-prone rail you will offer.

- **OFAC and sanctions screening before submission,** on every counterparty, every time — not just at vendor creation. Lists change.

- **Cutoff-time awareness.** ACH and wire have hard daily cutoffs and bank holidays. A payment scheduled for 4:59pm behaves differently from 5:01pm. This belongs in a calendar service, not scattered `if` statements.

### Funding and float

The uncomfortable structural question: when you pay a vendor $100,000 on behalf of a customer, whose money leaves first?

- **Pull-then-pay** — debit the customer, wait for settlement, then pay the vendor. Zero credit risk, but the vendor waits 3–5 extra days and your product feels slow.

- **Pay-then-pull** — pay the vendor immediately, debit the customer in parallel. Fast product, and you are exposed to the full amount if the debit returns.

Ramp is clearly in the second camp for at least some flows, which is exactly why they built an ML model for return probability and why their risk agents have dollar-denominated exposure budgets.

`[recommendation]` Launch pull-then-pay. Introduce pay-then-pull selectively, per customer, gated on observed repayment history and a hard per-customer exposure cap. The float is a lending decision disguised as a latency optimization, and treating it as a latency optimization is how AP startups die.

### Licensing reality

Moving customer money to third parties is money transmission in most US states. The common structures:

1. **Agent of the payee** — you contract with the *vendor* as their collection agent. Exempt in many states, requires vendor-side agreements at scale.

2. **Bank partnership** — the payment is made by a licensed bank; you are a technology service provider. Slower, more expensive, far cleaner.

3. **Get licensed** — 40+ state MTLs. Years, millions, ongoing examination burden.

Ramp's structure is not fully public. `[recommendation]` Assume option 2 for your build and price the bank partner into your model from day one. This is the item most likely to be discovered late and to invalidate a launch date. See `09-compliance-and-risk.md`.