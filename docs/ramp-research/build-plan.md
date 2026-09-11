# 10 — Build Plan

Everything in this file is `[recommendation]`. It is my sequencing, not a description of how Ramp did it.

## The honest scope assessment

Ramp reached ~$1B annualized revenue in six years with hundreds of engineers and billions in equity and debt. You are not going to reproduce that surface area in a year, and any plan that claims otherwise is a plan to build a shallow version of eight things instead of a deep version of two.

The useful question is not "how do I clone Ramp" but "what is the smallest thing that is genuinely useful, sits on the right foundations, and can grow into the rest."

The answer, in one sentence: **a ledger, a fund primitive, a card issuing integration, and a real-time authorization engine.** That is a real product. Everything else in this dossier is an extension of it.

## Buy versus build

The discipline comes from Ramp's own CTO: buy the commoditized layers, build the differentiation layer. Applied concretely:

| Component | Decision | Rationale |

|---|---|---|

| Card network | N/A | Visa/Mastercard. Not a choice. |

| Issuing bank / BIN sponsor | **Buy** | Requires a charter. Non-negotiable. |

| Issuer processor | **Buy** | Lithic or Stripe Issuing to start. Behind your own abstraction. |

| PAN vault | **Buy** | Never touch a PAN. This is the whole PCI strategy. |

| Card manufacturing / fulfillment | **Buy** | Via processor or bureau. It is a logistics business. |

| ACH / wire origination | **Buy** | Bank partner or Increase/Column/Modern Treasury. |

| Check printing | **Buy** | Lob or equivalent. Nobody should print checks. |

| International FX / payout | **Buy** | Wise, Airwallex, or bank corridor. |

| KYB / KYC / sanctions | **Buy** | Middesk, Persona, Alloy. Vendor-specific, list maintenance is their job. |

| Bank account verification | **Buy** | Plaid, MX, Teller. Also your underwriting data source. |

| Receipt / invoice OCR | **Buy** | Ramp buys this (Taggun). Commodity with a per-page price. |

| LLM inference | **Buy** | Behind a router. See Thompson sampling in `07`. |

| Data warehouse | **Buy** | Snowflake, BigQuery, or Databricks. |

| — | — | — |

| **Ledger** | **BUILD** | The core asset. Never outsource this. |

| **Fund / spend-control primitive** | **BUILD** | The differentiating abstraction. |

| **Real-time auth decisioner** | **BUILD** | Your product promise lives here. |

| **Receipt matching / entity resolution** | **BUILD** | OCR is bought; matching is the product. |

| **Coding / categorization engine** | **BUILD** | Rules + model + LLM ladder. |

| **Approval workflow engine** | **BUILD** | Ramp's graph engine. Highest reuse per unit of effort. |

| **ERP sync layer** | **BUILD** | Where finance-team trust is won or lost. |

| **Underwriting / risk models** | **BUILD** | Uses data only you have. Cannot be bought. |

The pattern: buy anything a vendor can do identically for everyone. Build anything whose quality is your product, or whose training data only you possess.

## Phase 0 — Foundations (months 0–3)

No customer-facing product. Do not skip it. Every phase after this one gets faster because of it, and retrofitting any of it is a rewrite.

**Engineering**

- Modular monolith scaffold. Python + Postgres. Type checking, linting, formatting, CI from commit one — Ramp published a whole post on retrofitting this and it was expensive.

- Tenancy model: business → entity → location → user, with `entity_id` on every financial table even though you launch single-entity.

- **The ledger.** Append-only, double-entry, deferred balance-check constraint trigger, multi-currency-aware. Nothing posts to it yet. Get it right now.

- Transactional outbox on Postgres. Ramp's lesson: 7 dropped tasks per 10,000 on a separate broker is unacceptable, and you cannot atomically commit state and enqueue work across two systems.

- OAuth2 server: client credentials + authorization code, prefixed tokens, scope model.

- Audit log at the write-dispatch boundary.

- `updated_at` cursor pagination on every list endpoint. This is the cheapest insurance in the entire plan.

- Idempotency-key handling on all POST/PATCH.

- Separate sandbox environment with seeded fixture data.

**Non-engineering, running in parallel and on the critical path**

- Engage fintech counsel.

- Begin processor selection and bank partner diligence. Bank diligence is 6–9 months and cannot be compressed by adding engineers.

- Draft the policy set: BSA/AML, sanctions, credit, fraud, vendor management.

**Exit criteria:** you can create a tenant, authenticate, and post a balanced multi-currency journal entry that survives a replay of the same idempotency key. A term sheet with a processor and a signed diligence engagement with a bank partner.

## Phase 1 — Cards and authorization (months 3–8)

The core product. Everything else is optional relative to this.

- Processor integration behind the `IssuingProvider` interface from `03-architecture.md`.

- Virtual card issuance. Iframe pattern for detail display — no PAN on your servers.

- **Fund** and **spend program** primitives: amount, interval, allowed categories, allowed merchants, allowed countries, shareable, permitted spend types. Fund creation auto-issues a card.

- **The authorization decisioner as a separate service.** p99 under 150ms, own replica, fail closed, hard internal timeout, no LLM, no cross-service calls.

- MCC → category mapping table as an in-process constant.

- Two-tier balance model: authoritative ledger plus fast available-balance store holding open authorization holds.

- Authorization hold lifecycle with mandatory expiry, reversal, partial clearing, incremental auth, and force-post handling.

- Clearing file ingestion, auth-to-clearing matching, ledger posting, interchange calculation.

- Transaction list and detail UI. Real-time spend feed off the auth stream.

- Physical card issuance and fulfillment.

- Employee onboarding: invite, roles, departments, locations, `USER_DRAFT` staging.

**Do not build in this phase:** receipts, coding, ERP sync, bill pay, reimbursements, approvals.

**Exit criteria:** an employee swipes a card at a merchant, the correct fund is selected, policy is enforced, the transaction appears in the dashboard in under two seconds, the hold expires correctly if never cleared, and the cleared transaction posts a balanced ledger entry. p99 auth latency under 150ms measured, not estimated.

**Launch here.** Prepaid or debit, funded from a customer balance — not charge. Zero credit exposure. See `09-compliance-and-risk.md` on why.

## Phase 2 — Expense management (months 8–12)

Turns a card into a product finance teams want.

- Receipt capture: mobile, SMS, email, Slack.

- OCR integration (bought) plus on-device extraction where available.

- **Receipt matching**: candidate retrieval, merchant alias resolution, locale-aware amount parsing, fuzzy matching, 2-of-3 auto-verify rule.

- Merchant normalization and alias table, seeded from network descriptors, grown from user corrections.

- Digital receipt auto-generation under the local substantiation threshold ($75 in the US). Highest-leverage feature in the phase and it involves no ML.

- Memos, receipt requirement policy, reminder automation, non-compliance escalation.

- Coding: the three-layer ladder — deterministic per-customer vendor→GL memory, then a global model, then an LLM for genuinely novel merchants only.

- Direct merchant receipt feeds for your top 20 merchants by transaction count. Beats OCR improvement on every dimension.

**Exit criteria:** a majority of transactions reach fully-coded, receipt-satisfied state with no human action.

## Phase 3 — Approvals and the workflow engine (months 10–14)

Overlaps Phase 2. Build it once, use it forever.

- Graph engine: vertices are actions or conditions, edges are dependencies, topological execution. **Multiple edges into a single vertex from the start** — the single-parent version is a dead end.

- Persist across ~10 tables, written in **one INSERT-CTE statement**. Row-by-row through an ORM is 20+ seconds; the single statement is under 200ms.

- Registered-configuration layer so new domain objects become conditionable without engine changes.

- A DSL/SDK that compiles `elif` chains into layered negated conditions.

- Visual builder driven by the same configuration.

- Approver matrix tables on a generic custom-records primitive, accepting natural keys (email, code, name) on write.

- External approval requests, so an outside system can be a node in the graph.

- Emit workflow state changes as events (`node_advanced`, `external_approval_request`, `override_approved`).

**Exit criteria:** approval routing, accounting field visibility, and conditional form building all run on the one engine, and adding a new routing policy requires no engine change.

## Phase 4 — Accounting and ERP sync (months 12–18)

Where adoption is won. Also where nothing is glamorous.

- Chart-of-accounts ingestion: GL accounts, custom fields, field options, accounting vendors, entities. 500-item all-or-nothing batches. Field before options.

- Three-state lifecycle on all reference data: active / hidden / inactive. Hidden stays syncable for historical records.

- Field option filter rules in disjunctive normal form — AND within a rule, OR across rules.

- The shared `NOT_SYNC_READY → SYNC_READY → SYNCED` state machine across transactions, bills, reimbursements, transfers, cashbacks.

- Two-phase bill sync (`BILL_SYNC` then `BILL_PAYMENT_SYNC`).

- `POST /accounting/syncs` with mandatory idempotency key, 5,000-item batches, `successful_syncs` / `failed_syncs`.

- **Error classification into user-actionable / transient / integrator-bug** before display. This is the difference between a self-service product and a support firehose.

- Connectors: QuickBooks Online → Xero → NetSuite → Sage Intacct. Build the generic accounting API *before* the second native connector, and make native connectors consume it.

- Multi-entity: `entity_id` scoping on reads, `entity_remote_ids` on uploaded options.

**Exit criteria:** an accountant closes a month using your product and the export requires no manual journal entries. Test this with a real accountant at real month-end.

## Phase 5 — Reimbursements (months 15–18)

Cheap, because it reuses everything.

- Reimbursement object, both directions (`BUSINESS_TO_USER` / `USER_TO_BUSINESS`).

- Full state machine including `FAILED_REIMBURSEMENT` and payment-specific states.

- Receipt-first creation: one endpoint that OCR-drafts a reimbursement when no ID is supplied.

- Mileage as a dedicated path.

- Multi-currency with all four amounts stored (line original, original total, business paid, payee received).

- Funds gate reimbursement eligibility — the same primitive as cards, so policy cannot drift.

- Payout via ACH, plus push-to-card for instant.

## Phase 6 — Bill Pay (months 18–26)

The biggest single expansion, and the first one with real money-transmission exposure.

- Vendor model: contacts, bank accounts, `accounting_vendor_remote_id` linkage.

- Bill object with **nested payment** — no independent payment endpoints. A payment cannot exist without an authorizing bill.

- Invoice ingestion: email intake, OCR extraction, draft bill.

- Duplicate invoice detection.

- **Card rail first.** It is easier, it monetizes via interchange, and it defers the licensing question.

- Then ACH, same-day ACH, check, wire, SWIFT.

- Every payment as a durable saga (Temporal), with return handling as a designed path, not an error branch.

- Sanctions screening before every release, not just at vendor creation.

- Cutoff-time and banking-calendar awareness in a dedicated service.

- **Bank account change controls**: out-of-band verification, second-admin notification, cooling-off period, prominent change display on the approval screen. Never exposed to an API token.

- No bill approval via API. No vendor creation via API. No bank account creation via API. These absences are the controls.

- Pull-then-pay funding to start. Pay-then-pull only per-customer, gated on repayment history and a hard exposure cap.

**Exit criteria:** a customer runs their full AP cycle in your product, and a returned ACH correctly reverses the ledger and notifies the right people without an engineer intervening.

## Phase 7 — Procurement (months 24–32)

- Custom intake forms with conditional logic, on the workflow engine.

- Spend requests, unified request objects, approval routing.

- Purchase orders with line items; PO-scoped single-use virtual cards.

- Item receipts.

- Two-way and three-way matching on shared `purchase_order_line_item_ids`. All three documents sharing the same line-item IDs is the verified match.

- Discrepancy blocking — payment held until resolved.

- Vendor agreements with contract parsing and renewal milestone events.

## Phase 8 — Treasury, travel, agents (months 30+)

Each is a product, not a feature. Sequence by customer demand, not by this list.

- **Treasury** — partner bank checking, brokerage/money market, balance history, auto top-up. Enables funding cards and bills from a balance you hold, which improves your float economics.

- **Travel** — the book-anywhere model where the card transaction is the enforcement point. Do not build a booking engine; partner for managed travel. Ramp partners with Melon and TravelPerk.

- **Agents / MCP** — an MCP server, agent identity inheriting user permissions, differential session lifetimes (1 week read-only, 24 hours read-write), Agent Cards as maximally-narrow single-use funds. Cheap if the fund primitive was built right in Phase 1. Expensive if it was not.

- **AI spend tracking** — a real product niche Ramp is already occupying.

- **App Center / partner platform** — distribution you don't pay for, and switching cost you don't have to engineer.

## Team shape

Approximate, at steady state through Phase 4:

| Function | Headcount | Notes |

|---|---|---|

| Backend / platform | 6–10 | Ledger, monolith, workflow engine |

| Authorization / payments | 2–3 | Owns the real-time path and its on-call |

| Integrations / ERP | 2–4 | Grows linearly with connector count. NetSuite alone can absorb two people |

| Frontend | 3–5 | |

| Mobile | 2 | Receipt capture is a mobile product |

| Data / ML | 2–4 | Matching, categorization, risk |

| Infrastructure / SRE | 2 | |

| Security | 1–2 | Not optional |

| **Compliance / risk ops** | **2–4** | **Not engineers. Not optional. Hire before launch, not after.** |

| Finance ops | 1–2 | Reconciliation, settlement, treasury ops |

The line most often missing from a clone plan is compliance and risk operations. Ramp automated theirs with agents *after* running it with humans and using those humans' decisions as the training set. You cannot skip to the automated version — there is no labeled data until humans have made the decisions.

## Cost envelope

Order of magnitude, US, through first eighteen months:

| Item | Range |

|---|---|

| Engineering (15–25 people, 18 months) | $5–12M |

| Compliance, legal, licensing counsel | $500K–2M |

| Bank partner setup and minimums | $100K–1M+ |

| Processor integration and minimums | $50K–500K |

| SOC 2 + PCI assessments | $100–300K |

| Vendor stack (KYB, OCR, Plaid, warehouse, LLM) | $200K–1M/yr |

| **Working capital for the receivable** (charge card) | **$10M–100M+, scaling with volume** |

That last line dominates everything above it and is why Ramp raised debt facilities rather than just equity. It is also the strongest argument for launching prepaid: it is the one line item you can set to zero by choosing a different product structure.

## Failure modes, ranked

1. **Building product before engaging a bank partner.** Their diligence is 6–9 months and gates launch. Nothing you build in parallel accelerates it.

2. **No ledger, or a late ledger.** Per-module balance tracking is the mistake you cannot recover from without a rewrite. Reconciliation debt compounds.

3. **LLM in the authorization path.** Guaranteed timeouts, which means network stand-in, which means policy bypass — the exact thing your customer paid you to prevent.

4. **PAN in your database.** Pulls your entire environment into PCI scope. Check your error tracker and your APM traces, not just your schema.

5. **Launching charge without underwriting.** At 50 bps net interchange, a 0.5% loss rate eliminates your gross revenue on that volume. Credit losses do not compress margin, they erase it.

6. **Limits on the card instead of a fund object.** You will be unable to express shared budgets, unable to gate reimbursements with the same policy, and unable to build Agent Cards cheaply.

7. **No `updated_at` cursor.** Free to design in, effectively impossible to retrofit, and a permanent tax on every partner integration. Ramp is living with this one.

8. **Underestimating NetSuite.** It is not one integration. It is one integration per customer.

9. **Building eight shallow modules instead of two deep ones.** A finance team will not tolerate a bill pay module that is 80% right. Depth beats breadth in this category, because the product's job is to be trusted with the general ledger.

10. **Hiring compliance and risk ops after launch.** There is no labeled data for automation until humans have made the decisions, and there is no launch until the policies exist.

## The one-paragraph version

Build a double-entry ledger, a fund primitive, and a fail-closed sub-150ms authorization decisioner behind a processor abstraction you own. Launch prepaid cards so your credit exposure is zero. Add receipt matching and coding, because that automation — not the card — is the product. Build the approval workflow engine once as a persisted graph and run everything on it. Win the accounting integration, because that is where a finance team decides to trust you. Then add AP, and only then consider charge terms, credit, and the rest. Engage a bank partner and counsel on day one, in parallel, because that timeline is the real critical path and no amount of engineering shortens it.

## Sources

See [sources.md](sources.md).