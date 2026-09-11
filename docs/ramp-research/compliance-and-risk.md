# 09 — Compliance, Security, and Risk

**Not legal advice.** Every path in this file requires counsel and, in most cases, a sponsoring bank whose compliance team will dictate the actual requirements. What follows is an engineering map of the obligations so you can architect for them rather than retrofit around them.

This is the file that kills clone projects. Not because the requirements are impossible, but because teams discover them in month nine.

## Onboarding: KYB and KYC

Ramp's published application model gives a precise picture of what must be collected.

### Application object

Required: `email`, `first_name`, `last_name` on the applicant.

Optional pre-fill fields:

| Field | Purpose |

|---|---|

| `application_type` | `RAMP_SUITE` (default) or `BILL_PAY_ONLY` |

| `business` | Business entity details |

| `financial_details` | Financial position |

| `controlling_officer` | The individual with control |

| `beneficial_owners` | Ownership structure |

| `ownership_acknowledgement` | Confirms all owners with **≥25% ownership** are included |

| `manual_bank_account` | External bank account **for underwriting** |

| `oauth_authorize_params` | Request OAuth authorization after invite acceptance |

### Status machine

```

STARTED → IN_REVIEW → { FOLLOW_UPS_REQUIRED | APPROVED | REJECTED | WITHDRAWN }

```

Webhooks fire on submission, approval, and rejection. One active financing application per business, so `GET` returns a single object rather than a list.

### What the schema tells you

The **25% beneficial ownership threshold** is not a Ramp product decision — it comes from FinCEN's Customer Due Diligence Rule (31 CFR 1010.230), which requires covered financial institutions to identify beneficial owners at 25% equity or greater, plus one individual with significant managerial control. That is `controlling_officer` and `beneficial_owners` in the schema. The `ownership_acknowledgement` field is the applicant's attestation of completeness, which is what shifts liability for an incomplete disclosure onto them.

`FOLLOW_UPS_REQUIRED` as a first-class state is the tell that manual review is normal, not exceptional. Automated KYB fails on a meaningful fraction of legitimate businesses — new entities with no filing history, complex ownership chains, trusts, foreign parents. Build the follow-up loop as a designed path with document upload, secure messaging, and SLA tracking. Do not build it as an error state.

`RAMP_SUITE` versus `BILL_PAY_ONLY` matters because **the two products have different diligence requirements.** A card program means extending credit and needs underwriting. Bill pay means moving customer money and needs money-transmission-grade diligence but not credit assessment. Tiering the application by product avoids collecting credit data from a customer who only wants AP.

### Minimum viable KYB pipeline

`[recommendation]`

```

1. Business identity — legal name, EIN, formation state, entity type,

registered address, incorporation documents

2. Registry verification — Secretary of State filing status, good standing

3. Beneficial owners — every ≥25% owner: name, DOB, SSN/ITIN, address, ID document

4. Controlling officer — the individual with significant managerial control

5. Sanctions screening — OFAC SDN, consolidated lists, PEP, adverse media,

on the business AND every individual

6. Bank verification — open banking (Plaid/MX/Teller) or micro-deposits;

doubles as the underwriting data source

7. Risk scoring — industry (MCC / NAICS) risk, geography, entity age,

cash flow pattern

8. Decision — approve / decline / manual review, with a recorded

rationale and the evidence that supported it

```

Requirements that are easy to miss and expensive to add later:

- **Ongoing screening, not one-time.** Sanctions lists change. Re-screen every counterparty on a schedule, and re-screen before every payment. A vendor legitimate at onboarding can be sanctioned next month.

- **Immutable audit trail of every decision** — what data was seen, which rules fired, who approved, when. Examiners ask for this and "we can reconstruct it from logs" is not an answer.

- **Retention.** BSA recordkeeping generally requires five years. Your deletion policy has to accommodate that, which interacts awkwardly with GDPR/CCPA erasure requests. Resolve this with counsel before you write the deletion job.

## Money transmission

The structural question: moving customer funds to third parties is money transmission in most US states.

Three structures:

| Structure | Description | Cost |

|---|---|---|

| **Agent of the payee** | You contract with the *vendor* as their collection agent. Exempt in many states. | Requires vendor-side agreements at scale; state-by-state analysis |

| **Bank partnership** | The bank makes the payment; you are a technology service provider | Slower, revenue share, cleaner |

| **Own licenses** | 40+ state MTLs | Years, millions, ongoing examination |

Ramp's exact structure is not fully public. Their bank partners are: **Celtic Bank** and **Sutton Bank** (card issuing), **First Internet Bank of Indiana** (deposits, FDIC insurance), **Apex Clearing** (brokerage).

`[recommendation]` Assume bank partnership and price it into the model from day one. This is the single item most likely to be discovered late and invalidate a launch date. Engage a bank partner before you write payment code, because their compliance requirements will shape your data model — required fields, screening timing, transaction monitoring thresholds, reporting formats.

Note also: FDIC insurance requires a bank. If you tell customers their balance is insured, that insurance comes from the partner bank's coverage passed through, and the pass-through arrangement has specific requirements about account titling and recordkeeping that must be in your schema.

## PCI DSS

The rule that should govern every design decision here: **any system component that stores, processes, or transmits cardholder data is in PCI DSS scope**, and scope is contagious — a system connected to an in-scope system is generally in scope too.

### Ramp's scope-reduction architecture

Two published patterns, and the distinction is entirely about PCI scope:

**Iframe / embedded cards.** Your backend mints a short-lived token; a provider-served iframe renders card details directly to the user's browser. Ramp's documentation states plainly: *"Your service is out of scope on the data plane."* Origin must exactly match `window.location.origin` and a pre-verified origin. New integrations load a business-scoped URL, not the root domain.

**Vault API.** `POST /cards/vault` returns a full `pan` and `cvv` server-side. Requires `cards:read_vault` + `limits:write`, **plus production approval after Ramp reviews use case, security controls, and PCI handling.** Sandbox is open to all. Published handling rule: *"Use card details only transiently for the approved payment flow. Do not store or log PANs or CVVs."*

`[recommendation]` The architecture follows directly:

- **No PAN column in your database. Ever.** Not encrypted, not tokenized-but-reversible. The PAN lives at the processor; you store an opaque reference. This is why the `card` table in `02-domain-model.md` has `last_four`, `exp_month`, `exp_year`, and `processor_ref` and nothing else.

- **Default every user-facing flow to the iframe pattern.** The PAN goes processor → browser, never touching your servers. This can reduce your assessment from a full Report on Compliance to SAQ-A territory, which is the difference between a compliance program and a questionnaire.

- **Gate server-side PAN retrieval behind a scope, a human approval, and an audit event on every call.** Copy Ramp's model exactly. If a machine genuinely must present a PAN (automated checkout, agent purchase), hold it in memory for the duration of one HTTP call and never write it anywhere — not to a log, not to a metric label, not to an APM trace, not to a crash dump.

- **Audit your observability stack specifically.** Datadog, Sentry, and structured loggers capture request bodies by default. The most common PAN leak is not a database column; it is an error tracker that serialized the request payload on an exception.

## Regulatory surface by product

| Product | Regime |

|---|---|

| Charge card | Commercial credit. Reg Z largely exempts business-purpose credit, but not entirely, and card network rules apply regardless |

| Deposits | FDIC pass-through via partner bank; account titling and recordkeeping requirements |

| Investment account | Securities regulation, SEC/FINRA, via broker-dealer partner (Apex for Ramp) |

| ACH origination | NACHA Operating Rules — authorization, return handling, WEB/CCD/PPD entry classes |

| Wire | Fedwire/CHIPS rules, OFAC screening before release |

| International | FinCEN, correspondent banking, local licensing per corridor |

| Stablecoin payout | Fast-moving. Depends on jurisdiction and stablecoin issuer. Get specific advice |

| All money movement | BSA/AML program, SAR filing, CTR where applicable, transaction monitoring |

| All of it | State-by-state analysis |

Plus the audit and certification burden customers will demand:

- **SOC 2 Type II** — table stakes to sell to any company with a security review. Budget 6–12 months to first report.

- **PCI DSS** — level determined by transaction volume.

- **SOX support** — enterprise customers subject to SOX need your controls documented and your audit trail complete. Ramp sells SOX customization at the enterprise tier.

- **GDPR / CCPA** — data subject rights, in tension with BSA retention.

## Underwriting and credit risk

The business hiding inside the card business.

### The exposure

In a charge card program, **you settle with the network before your customer pays you.** Between settlement and repayment you hold unsecured exposure to every customer, for their full cycle spend. There is no collateral and no security interest.

### Ramp's controls, as far as they are public

**Cash-flow underwriting.** The application collects a `manual_bank_account` explicitly "for underwriting" — reading actual bank balances and transaction history rather than relying on a credit bureau. For a three-month-old startup with no credit file, observed cash position is the only real signal.

**ML return prediction.** Ramp's engineering blog names the exact mechanism: deciding when to release a payment depends on modeling "the probability of a debit returning," trained on "millions of historical data points." An ACH R01 (insufficient funds) arriving days after you have settled with the network means you are unsecured for the full amount.

**Exposure budgets.** Automated risk decisions carry a cap on "total dollar risk they can carry at once," raised incrementally as confidence grows.

**Governed policy.** Every autonomous decision is auditable and "governed under an approved policy" — decisions delegated to models and deterministic policy, never to free-form agent reasoning. See `07-ai-ml-and-agents.md`.

### What you need before launching charge

`[recommendation]`

1. **Onboarding underwriting** — bank-verified cash position, entity age, industry risk. Set an initial limit as a function of observed liquidity, not of ambition.

2. **Continuous re-underwriting** — daily re-read of the linked account. Cash position falling is your leading indicator, and it is available days before a return.

3. **Hard exposure caps** — per-customer daily and cycle limits, independent of the sum of their fund limits. A customer with $500k of fund limits should not be able to spend $500k on day one of their relationship.

4. **Concentration limits** — cap exposure to any single customer as a percentage of your capital, and cap aggregate exposure to any single industry.

5. **A loss reserve** — funded from revenue, sized from observed loss rates, before you need it.

6. **A collections path** — because some customers will not pay.

`[recommendation]` **Launch prepaid or debit, not charge.** Spend draws from a customer-funded balance; your credit exposure is zero. Graduate customers to charge terms as you accumulate cash-flow history and can underwrite them properly. This inverts Ramp's sequence, but Ramp raised billions of dollars of equity and debt facilities to fund the receivable. Without that balance sheet, launching an unsecured charge product to unknown SMBs is not a product risk, it is a solvency risk.

The uncomfortable arithmetic: at 50 bps net interchange, a **0.5% loss rate on your receivable wipes out your entire gross revenue on that volume.** Credit losses do not reduce your margin; they eliminate it. This is why the underwriting is not a compliance checkbox but the actual core competency of the business.

## Fraud

Distinct from credit risk. Credit risk is a customer who cannot pay. Fraud is someone who never intended to.

| Vector | Control |

|---|---|

| **Stolen card / testing** | Velocity rules, CVV/AVS checks, 3DS challenge, device fingerprinting, decline patterns |

| **Account takeover** | MFA (mandatory for admins), session anomaly detection, step-up on sensitive actions, notification on credential change |

| **Business email compromise** | Vendor bank-account change verification. **The highest-value attack in AP.** See below |

| **Fake invoice** | Duplicate detection, PO matching, three-way match, vendor allowlist |

| **Synthetic identity onboarding** | Device and behavioral signals at application, cross-customer identity graph |

| **Insider / employee** | Spend policy enforcement, receipt requirements, dual control on money movement, complete audit log |

| **Agent/API abuse** | Scope minimization, short-lived write sessions, exposure budgets, per-user permission inheritance |

### Business email compromise is the one to obsess over

BEC works by changing a **legitimate** vendor's bank details, not by creating a fake vendor. The invoice is real, the vendor is real, the approval is real — only the destination account is wrong. Every downstream control passes.

Look at what Ramp's API deliberately omits: **no `POST /vendors`, no vendor bank account creation via API, no entity bank account management via API, and no bill approval via API.** Those absences are not gaps in the roadmap. They are the controls.

`[recommendation]` Whatever else you build, make bank-account changes require: out-of-band verification (micro-deposit or open-banking validation of account ownership), notification to a second admin, a cooling-off period before the new account can receive its first payment, and a UI that displays "this vendor's bank details changed 2 days ago" prominently on the payment approval screen. And never expose the mutation to an API token.

## Security architecture

`[recommendation]` — baseline for a financial system.

**Tenant isolation.** Row-level security in Postgres, or a mandatory `business_id` predicate enforced at the data-access layer where it cannot be forgotten. A cross-tenant data leak in a financial system is an existential event, and the most common cause is a query someone wrote without the tenant filter. Make it structurally impossible, not conventionally avoided.

**Secrets.** Every processor credential, bank credential, and signing key in a managed secret store with rotation. Never in environment variables in a container image, never in a repo.

**Least privilege at runtime.** Ramp published work on "just-in-time access to cloud resources" — engineers request scoped, time-limited access rather than holding standing production credentials. Adopt this early; retrofitting it means taking access away from people who have grown used to having it.

**Audit everything, at the boundary.** Ramp's agent documentation notes that every write action lands in the customer's audit log "automatically, no extra wiring." That phrasing matters: audit logging is at the write dispatch boundary, not in each handler. Handler-level audit logging is audit logging with holes in it.

**Dual control on money movement.** Two humans for any payment above a threshold, and for any change to payment destination. Enforced in the workflow engine, not in UI conditionals.

**Encryption.** TLS 1.2+ everywhere including internal service-to-service. Encryption at rest. Field-level encryption for SSN, DOB, and bank account numbers — separate keys from the database encryption key, so a database dump is not sufficient.

**Immutable logs.** Append-only, tamper-evident, shipped off-host in real time. An attacker who can edit your audit log has erased the incident.

## The compliance timeline you should actually plan for

`[recommendation]` A realistic sequence, and the reason `10-build-plan.md` looks the way it does:

| Months | Activity |

|---|---|

| 0–3 | Engage counsel. Select and begin diligence with a bank partner and processor. Model the licensing structure. |

| 3–9 | Bank partner diligence: they audit your controls, your policies, your BSA/AML program, your key personnel. This is the long pole and it is not parallelizable by adding engineers. |

| 6–12 | Write and adopt the actual policy set: BSA/AML program, sanctions, credit, fraud, complaint handling, vendor management, business continuity. Appoint a compliance officer. |

| 9–15 | SOC 2 Type II observation window and first report. |

| 12+ | PCI assessment at the level your volume dictates. |

Nothing in that table is engineering work, and none of it can start after the product is built. The teams that fail at this build a working product in twelve months and then discover they cannot launch it for another twelve.

