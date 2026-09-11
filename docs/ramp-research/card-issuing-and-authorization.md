# 04 — Card Issuing and Real-Time Authorization

The hardest part of the build. Everything else in the platform tolerates seconds or minutes. This tolerates about one second, and being wrong is visible to your customer's employee standing at a checkout.

## The issuing stack

Four layers, and you will buy at least three of them.

```

┌──────────────────────────────────────────────────────────┐

│ YOU — program manager + automation layer │ BUILD

│ funds, policy, controls, receipts, coding, UX │

├──────────────────────────────────────────────────────────┤

│ ISSUER PROCESSOR │ BUY

│ card lifecycle, PAN vault, auth stream, clearing files │

│ Marqeta (Ramp's choice) / Lithic / Stripe Issuing / │

│ Galileo / Highnote / i2c │

├──────────────────────────────────────────────────────────┤

│ ISSUING BANK / BIN SPONSOR │ BUY

│ holds the BIN, network membership, regulatory owner │

│ Celtic Bank + Sutton Bank (Ramp's) / WebBank / │

│ Cross River / Evolve / Column │

├──────────────────────────────────────────────────────────┤

│ CARD NETWORK — Visa / Mastercard │ N/A

│ interchange rules, ISO 8583 messaging, settlement │

└──────────────────────────────────────────────────────────┘

```

Ramp's actual configuration, as publicly stated: **Ramp Visa Corporate Card issued by Celtic Bank; Ramp Visa Commercial Card issued by Sutton Bank; Marqeta as issuer processor.** Two banks, not one — because different card products, geographies, and program economics need different sponsors, and because single-sponsor concentration is an existential risk.

### Why you buy the middle layers

Historically, issuing a card meant being a chartered bank, then contracting a managed service provider — TSYS, First Data, i2c — described by Ramp's CTO as "a blend of services and technology" with "their own hardware." It "took a lot of time and it took a lot of money."

Modern issuer processors abstracted the bank-network relationship behind APIs with variable-cost pricing. That is what made a Ramp possible in 2019 and what makes your clone possible now.

### How to choose a processor

Ramp's stated criteria, in their order of importance:

1. **Roadmap alignment and velocity** — deemed *most* important, because "most of the value... is going to come over the next five or 10 years." You are picking a co-development partner, not a commodity supplier.

2. **Use-case and network support** — differs by Visa versus Mastercard, prepaid support, virtual bank account creation, consumer versus business focus.

3. **API quality and documentation** — modern players offer cleaner APIs; legacy players have outdated integrations.

Plus two dimensions of scalability worth separating:

- **Technical scalability** — does the platform hold under your transaction and card volume.

- **Business-model scalability** — do the unit economics hold at scale. Larger processors have supplier-cost leverage that smaller ones do not.

The tradeoff with smaller providers (Lithic, and historically Bond and Unit) is operational maturity — card manufacturing, bank relationship management — exchanged for closer engineering access and faster iteration for a small team.

`[recommendation]` For a clone starting now: **Lithic or Stripe Issuing** for speed to first swipe. Both support real-time authorization webhooks, which is the non-negotiable feature. Then build the abstraction described in `03-architecture.md` so you can add Marqeta or a direct bank relationship when volume justifies renegotiation.

### The economics you are inheriting

- Total interchange on a commercial card transaction: roughly **250 bps** (varies materially by MCC, card product, and transaction type).

- Issuing bank's share: roughly **200 bps**.

- Your net: roughly **50 bps**.

At 50 bps you need **$200M of annual card volume to generate $1M of revenue.** That single number should drive your entire go-to-market. It also explains why Ramp gives the software away: software revenue per customer is small relative to interchange on that customer's spend, so the software's job is to capture spend share.

Card-present, card-not-present, and international transactions carry different interchange. Ramp offers 1.5% cashback against roughly 50 bps of net interchange, which means **cashback is funded out of gross interchange before the bank split, not out of net revenue** — the arithmetic only works with a favorable sponsor agreement. `[inferred]` Do not model 1.5% cashback against 50 bps net; you will be underwater on every transaction.

## The authorization path

This is the critical path. Get it right.

### Message flow

```

1. Employee swipes / enters card online

2. Merchant → acquirer → Visa/Mastercard → issuing bank → issuer processor

3. Processor calls YOUR webhook with an authorization request

── you have ~1 second, sometimes less ──

4. You return APPROVE or DECLINE (+ reason code, + optional partial amount)

5. Processor responds to the network

6. Merchant sees approved or declined

7. Later (hours to days): clearing/presentment file settles the transaction

8. Later still: settlement funds move

```

If you do not answer in time, the network applies **stand-in processing** and decides on your behalf using rules configured at the bank or processor. Stand-in approvals bypass your entire policy engine — spend gets through that your customer explicitly blocked. Timeouts are therefore not a degraded mode, they are a **policy bypass and a security incident**.

`[recommendation]` Configure stand-in to **decline** for a spend management product, and treat every stand-in event as a paged incident. A false decline is a support ticket. A stand-in approval on a blocked merchant is a broken promise to your customer.

### Latency budget

```

Total network tolerance ~2000 ms (processor-dependent, sometimes 1000)

− network transit both ways ~200 ms

− processor overhead ~100 ms

────────────────────────────────────────

Your budget ~700 ms realistic target

Your p99 target 150 ms

Your hard internal timeout 400 ms → fail closed to DECLINE

```

What this budget forbids, absolutely:

- **No LLM calls.** Not for categorization, not for anomaly detection, not for anything. Ramp's own risk architecture makes this explicit: agents orchestrate, but "risk-based decisions are often predictions in disguise" and are delegated to pre-trained models invoked as tools. Any ML in the auth path must be a compiled model doing sub-10ms local inference on pre-computed features, or it must be out of the path entirely.

- **No cross-service network calls.** Every input must be in local memory, local cache, or a co-located replica.

- **No unbounded queries.** No `SUM()` over a transaction table. Interval spend must be a pre-aggregated counter.

- **No writes on the read path** beyond a single append of the auth record and a counter increment, ideally in one transaction.

### Decision algorithm

Evaluate in cost order — cheapest, most-likely-to-decline checks first, so the expensive ones rarely run.

```python

def decide(req: AuthorizationRequest) -> AuthDecision:

# 0. Idempotency — processors retry

if prior := auth_store.get(req.processor_auth_id):

return prior.decision

# 1. Card lookup — hot cache, must not miss

card = card_cache.get(req.card_token)

if card is None:

return Decline(NETWORK_ERROR) # fail closed, page immediately

if card.state != ACTIVE:

return Decline(CARD_INACTIVE)

# 2. Cardholder state

if card.cardholder.status not in (USER_ACTIVE,):

return Decline(CARD_INACTIVE)

# 3. Fund selection — a primary card may link multiple funds

funds = fund_router.eligible(card, req) # ordered by priority

if not funds:

return Decline(NO_ELIGIBLE_FUND)

for fund in funds:

if fund.status != ACTIVE:

continue

# 4. Categorical restrictions — pure in-memory set membership

category = MCC_TO_CATEGORY[req.mcc] # static map, no I/O

if fund.allowed_categories and category not in fund.allowed_categories:

continue

if fund.allowed_merchants and req.merchant_id not in fund.allowed_merchants:

continue

if fund.allowed_countries and req.country not in fund.allowed_countries:

continue

# 5. Amount / velocity — pre-aggregated counter for the current interval

spent = balance_store.interval_spend(fund.id, fund.interval) # includes open holds

if spent + req.amount > fund.limit_amount:

# partial authorization if the network and merchant allow it

if req.supports_partial and (headroom := fund.limit_amount - spent) > 0:

return ApprovePartial(headroom, fund)

continue

# 6. Fraud score — pre-computed features, local model, <10ms, or skip

if fraud_model.score(req, card) > THRESHOLD:

return Decline(SUSPECTED_FRAUD)

# 7. Business-level funding check (charge card credit line / account balance)

if not funding.has_headroom(card.business_id, req.amount):

return Decline(INSUFFICIENT_FUNDS)

return Approve(fund, hold_id=place_hold(fund, req))

return Decline(POLICY_VIOLATION)

```

Points worth flagging:

- **Fail closed.** Every unexpected condition declines. A wrongly-declined transaction is recoverable; a wrongly-approved one is a policy violation you promised to prevent.

- **Fund routing before restriction checks.** Because a primary physical card can draw from multiple linked funds with automatic routing, the loop tries each in priority order. A lodging charge should find the travel fund even if the software fund is first in the list.

- **Category mapping is a static in-process map.** The MCC arrives on the wire as 4 digits; your category groups (meals=19, lodging=6, airlines=4 in Ramp's numbering) are a compile-time constant, not a database lookup.

- **Partial authorization** matters at fuel pumps and for split-tender retail. Supporting it turns a hard decline into a completed purchase.

- **The hold, not the ledger.** Approving places a hold in the fast balance store. Nothing posts to the accounting ledger yet — an authorization is a reservation, not an accounting event.

### Holds and their lifecycle

This is where clone implementations most commonly leak money.

```

AUTHORIZED ──► CLEARED (presentment matches, hold released, ledger posts)

│

├──────► REVERSED (merchant reverses; release hold immediately)

│

├──────► EXPIRED (no presentment within N days; release hold)

│

└──────► PARTIALLY_CLEARED (cleared amount < authorized; release difference)

```

Rules you must implement:

- **Expiry is mandatory.** Authorization holds must expire on a timer (typically 5–7 days, varies by MCC — hotels and car rentals run much longer). If you never expire holds, funds silently exhaust and customers see declines with budget remaining.

- **Cleared amount ≠ authorized amount.** Restaurants authorize the pre-tip amount and clear with tip. Hotels place an incremental estimate and clear the final folio. Fuel pumps authorize $1 and clear the fill. Your clearing matcher must handle a cleared amount both **below and above** the authorized amount.

- **Incremental authorizations** on the same original auth ID must aggregate, not create parallel holds.

- **Force posts** arrive with no prior authorization at all — offline terminals, airline in-flight sales. You must accept them; you cannot decline a force post. Budget for the overage.

- **Matching is by processor auth ID first, then heuristically** (card + merchant + amount + date window) when the ID is absent.

`[recommendation]` Model the open-authorization table explicitly with its own state machine and a background reconciler. Do not treat a hold as a mutable field on the transaction row. You will need the history to explain a balance discrepancy to a customer.

## Card issuance

### Two delivery patterns for virtual card details

Ramp exposes both, and the distinction is a PCI scope decision, not a convenience.

**Pattern A — Ramp-served iframe (embedded cards).** Your backend mints a short-lived token; your frontend loads a provider-served iframe; the iframe renders card details directly to the user. Your service is explicitly "out of scope on the data plane." The hosting page's origin must exactly match `window.location.origin` and a pre-verified origin. Ramp's new integrations must load a business-scoped URL (`https://embed.ramp.com/business/{business_id}`) rather than the root domain.

**Pattern B — Vault API (server-side PAN retrieval).** `POST /cards/vault` creates a fund, issues a virtual card, and returns a full `pan` and `cvv` in one request. Requires the `cards:read_vault` scope **plus** `limits:write`, and — critically — **production access requires review of your use case, security controls, and PCI handling.** Sandbox is open to all customers.

Handling rule as published: *"Use card details only transiently for the approved payment flow. Do not store or log PANs or CVVs."*

`[recommendation]` Default to Pattern A for every user-facing flow. Pattern B is only justifiable when a machine, not a human, must present the PAN — automated checkout, agent purchases. Every server that touches a PAN pulls your entire environment into PCI DSS scope, and that is a compliance program, not a code change.

### Card lifecycle

Ramp's published model is notable for what it does *not* expose. There is no direct card-freeze API and no direct card-terminate for vault cards — instead you **terminate the underlying fund** with `DELETE /developer/v1/funds/{fund_id}`, which is synchronous, irreversible, and "can affect every card or member attached to that fund."

`[inferred]` That is a coherent consequence of the fund-centric model: the fund is the unit of authority, and the card is a credential against it. Killing the authority kills every credential. It is also a footgun the docs warn about explicitly.

`[recommendation]` Expose both. Card-level `lock`/`unlock`/`terminate` for the "I lost my card" case, and fund-level termination for the "this program is over" case. Ramp's model forces the wrong tool for the common case.

### Physical card fulfillment

The parts you will underestimate:

- Card manufacturing and personalization — handled by the processor or a bureau (IDEMIA, Thales, Arroweye).

- Shipping and tracking, including expedited and international.

- Activation flow with identity binding.

- Replacement for lost/stolen/damaged, with PAN rotation and re-provisioning of wallet tokens.

- Expiry and reissuance cycles — a batch process that runs forever and must not break wallet provisioning or recurring merchant billing.

- Card art and embossing constraints.

Ramp's answer on the last point: smaller processors trade away card manufacturing and bank relationship management. If your processor does not run fulfillment, you are running a logistics operation.

### Wallet provisioning and 3DS

Both are required, neither is optional in 2026:

- **Apple Pay / Google Pay push provisioning** — the in-app "add to wallet" flow. Requires network-specific certification.

- **3D Secure (3DS2)** — Ramp enrolls cards for international and online use. You need a challenge flow: a step-up authentication delivered to the cardholder, which means push notification or SMS infrastructure in the authorization path with a human in the loop. This is a separate real-time system from auth decisioning and it has its own latency and UX problems.

## Clearing and settlement

```

Daily: processor delivers clearing/presentment file

│

├─► match each record to an open authorization

├─► create or update the transaction record

├─► release / adjust the hold

├─► post the accounting entry to the ledger

├─► compute interchange earned

├─► accrue cashback liability

└─► emit transactions.cleared event → downstream (coding, receipt matching, sync)

```

Then settlement: net funds move between you, the bank, and the network on the network's settlement cycle. **Your obligation to settle is independent of whether your customer has paid you.** That gap is the working capital requirement of a charge card program, and it is the single largest capital item in the business.

### The charge card repayment loop

Ramp's card is a charge card: balances are paid in full on a cycle rather than revolving.

```

Card spend accrues → statement cycle closes → ACH debit pulled from the

customer's linked external bank account → funds arrive (or return)

```

The risk is the **ACH return**. An R01 (insufficient funds) days after you have already settled with the network means you are unsecured. Ramp's engineering blog names this exact problem: deciding when to release a payment depends on modeling "the probability of a debit returning," which they treat as a machine learning problem rather than a rule.

That is the crux of the credit business hiding inside the card business. You extend intraday-to-monthly unsecured credit to every customer, and your only protections are:

1. **Underwriting at onboarding** — Ramp collects a `manual_bank_account` for underwriting during the application flow, meaning they read actual bank balances and cash flow rather than relying on a credit bureau.

2. **Dynamic limit management** — continuously re-underwriting from observed cash position.

3. **Return prediction** — the ML model above, gating payment release.

4. **Velocity and concentration controls** — capping single-day exposure per customer.

`[recommendation]` Do not launch the charge card until you have items 1 and 4. Items 2 and 3 require data you will not have on day one. Consider launching **prepaid/debit first** — spend draws from a customer-funded balance, so your credit exposure is zero — and graduate customers to charge as you accumulate cash-flow history. This inverts Ramp's order but is the only responsible sequence without Ramp's balance sheet.

