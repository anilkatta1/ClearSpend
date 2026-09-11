# 02 — Domain Model

Reconstructed from Ramp's OAuth scope list (which is effectively a resource inventory), the webhook event catalog, and the per-domain developer guides. Field names and enum values quoted here are Ramp's actual published names.

## The resource inventory

Ramp's OAuth scopes enumerate the platform's top-level resources almost exactly. The complete published list:

```

accounting:read/write applications:read/write bank_accounts:read/write

bills:read/write budgets:read business:read

cards:read/write/read_vault cashbacks:read custom_records:read/write

departments:read/write entities:read funds:read/write

incorporation:read/write item_receipts:read/write limits:write

locations:read/write memos:read/write merchants:read

purchase_orders:read/write receipt_integrations:r/w receipts:read/write

reimbursements:read/write spend_programs:read/write statements:read

tasks:read transactions:read/write transfers:read

treasury:read users:read/write vendors:read/write

```

Note `limits:write` surviving alongside `funds:read/write`. This is legacy naming: what Ramp now calls a **Fund** was previously a **Limit**, and the API still accepts a fund ID in the `limit_id` filter on the transactions endpoint. Vestigial naming like this is a reliable tell that Funds are the older, deeper primitive in the system — plan yours as a first-class aggregate, not a late addition.

## Bounded contexts

Group the resources into contexts before you write schema. These map cleanly onto service boundaries later.

| Context | Owns |

|---|---|

| **Identity & Tenancy** | business, entity, location, department, user, role, session |

| **Spend Controls** | fund, spend_program, approval policy, workflow definition |

| **Card & Authorization** | card, authorization, decline, merchant, MCC mapping |

| **Ledger** | account, journal_entry, posting, balance snapshot |

| **Transactions & Expense** | transaction, receipt, memo, coding assignment |

| **Reimbursements** | reimbursement, line item, mileage claim, payout |

| **Payables** | vendor, vendor_contact, vendor_account, bill, bill_line_item, bill_payment |

| **Procurement** | spend_request, custom_form, purchase_order, po_line_item, item_receipt, vendor_agreement |

| **Approvals** | unified_request, workflow node, external approval request |

| **Accounting** | connection, gl_account, field, field_option, filter_rule, accounting_vendor, tax_code, tax_rate, inventory_item, coding, sync |

| **Treasury** | banking_account, balance_history, transfer, statement, cashback |

| **Onboarding & Risk** | application, controlling_officer, beneficial_owner, external bank_account |

| **Platform** | webhook_subscription, task, audit_log_event, api_client, custom_record |

## Tenancy model

Four levels, and getting this wrong is expensive to unwind:

```

business (tenant root)

└── entity (legal entity / subsidiary — the accounting and payment boundary)

└── location

└── user

└── department (orthogonal to location)

```

The critical published detail: **a user's `entity_id` is derived from their `location_id`.** Entity is not set directly on the user. Locations map to entities; users map to locations. That indirection means an org restructure is a location remap, not a mass user update.

Entity is the boundary that matters for money movement — bills carry an `entity_id` and a `source_bank_account_id` drawn from that entity's accounts. Multi-entity is not a reporting feature bolted on later; it is a foreign key on every financial object. Put `entity_id` on your financial tables from day one even if you launch single-entity. `[recommendation]`

### User model

Published fields: `role`, `department_id`, `location_id`, `direct_manager_id`, `entity_id`.

Role enum: `BUSINESS_USER`, `BUSINESS_ADMIN`, `BUSINESS_BOOKKEEPER`, `IT_ADMIN`, `AUDITOR`, `GUEST_USER`. `BUSINESS_OWNER` exists but cannot be created via API.

Status enum, all five:

| State | Meaning |

|---|---|

| `USER_DRAFT` | Record exists, no invite sent |

| `INVITE_PENDING` | Invite sent, not accepted |

| `USER_ACTIVE` | Onboarded, can transact |

| `USER_INACTIVE` | Cards frozen, spend blocked, cannot log in; record preserved for history and reactivation |

| `USER_SUSPENDED` | Suspended by the platform for risk or policy; not settable by API callers |

Two design points worth stealing. First, `USER_DRAFT` lets an HRIS push a full org chart before anyone is invited — provisioning and activation are decoupled. Second, deactivation is a state transition that freezes cards and preserves history, never a delete. Financial records must survive employee departure. `AUDITOR` and `GUEST_USER` as first-class roles reflect that external accountants and contractors are real users, not edge cases.

User creation is **asynchronous**: `POST /developer/v1/users/deferred` returns a task id, polled at `GET /developer/v1/users/deferred/status/{task_id}` with statuses `STARTED`, `IN_PROGRESS`, `ERROR`, `SUCCESS`. Most complete in under 5 seconds. `[inferred]` The async shape exists because user creation fans out to the card processor, the identity provider, and email delivery — none of which you want inside a synchronous HTTP request.

## Spend Controls — the core primitive

This is the most important part of the model and the least obvious. Three primitives:

### Fund

> "A budget with restrictions — amount, interval (daily, monthly, total), allowed merchant categories, allowed merchants, allowed countries."

Key behaviors:

- **Every card draws against a fund.** The fund, not the card, holds the budget.

- Creating a fund **automatically issues a virtual card**. The 201 response contains the fund's `id` and its auto-issued card in `cards`.

- A fund can be attached to physical cards as well.

- A primary physical card can draw from **multiple active linkable funds** with automatic routing, when primary-card spending is enabled.

- Funds **also gate reimbursements** when no card is involved. A fund with no card is reimbursement-only.

- Lifecycle: create, update, suspend, terminate. Termination is irreversible and affects every card and member attached.

- Members: `POST`/`DELETE /developer/v1/funds/{fund_id}/members`. A fund requires an initial `user_id`.

Interval enum (published across two guides): `DAILY`, `MONTHLY`, `ANNUAL`, `TOTAL`, and "etc."

### Spend Program

A template that mass-produces funds with consistent policy. Published fields:

- `display_name`, `description` — visible to users and reviewers

- `is_shareable` — whether one fund can be shared by multiple users

- `permitted_spend_types` — includes `primary_card_enabled`, `reimbursements_enabled`

- `spending_restrictions` — `limit` (amount, currency), `interval`, `allowed_categories`

Categories are integer-coded: the docs give meals = 19, lodging = 6, airlines = 4. `[inferred]` These are Ramp's own category groupings over MCC ranges, not raw MCCs — a swipe carries a 4-digit MCC, and you need a mapping table from MCC to human-meaningful category group.

**The binding is fixed at mint time.** Funds inherit the program's policy at creation, and changing policy requires terminating and re-minting. That is a deliberate immutability choice: it means a fund's restrictions cannot silently change under a cardholder mid-cycle, and an authorization decision can be reasoned about from the fund alone. It is also a real limitation — bulk policy updates are impossible.

`[recommendation]` Copy the template/instance split, but consider versioning the program and letting funds pin a version with an explicit migration operation. You get Ramp's auditability without its rigidity.

### Approvals

The review path a spend action travels. Routes bills, reimbursements, purchase orders, and fund-creation requests. Can be native or delegated to an external system ("Blank Canvas" approvals, `blank_canvas:write` scope).

### Why this design is right

The non-obvious insight: **the budget is not on the card and not on the user.** It is a separate object that cards, users, and reimbursements all reference. This is what makes "give the marketing team $50k/quarter for conferences, spendable by six people, on four categories, in two countries, via one shared virtual card and out-of-pocket reimbursement" a single object rather than a policy engine special case.

If you model limits as columns on the card table, you will discover you cannot express shared budgets, cannot gate reimbursements with the same policy, and cannot issue a replacement card without re-deriving policy. Model the fund first.

## The three-vendor problem

Ramp maintains **three distinct counterparty entities**, and understanding why is the difference between a clean accounting integration and a permanent data-quality problem.

| | **Merchant** | **Vendor** | **Accounting Vendor** |

|---|---|---|---|

| What it is | Card transaction counterparty | Bill Pay payee | GL coding value |

| Created by | Card network, automatically | User or API | ERP sync or API |

| Scope | Global, all businesses | Per-business | Per-business, per-ERP-connection |

| Mutable | No, read-only | Yes, full CRUD | Yes, full CRUD |

| Bank accounts | No | Yes | Yes |

| API path | None — embedded on transaction | `/developer/v1/vendors` | `/developer/v1/accounting/vendors` |

| Anchor product | Cards | Bill Pay | ERP Integrations |

Merchant surfaces on a transaction as `merchant_id` and `merchant_name`, with normalized name, logo, and category code. It has no create/update/delete.

**There is no direct foreign key between Merchant and Vendor.** The Accounting Vendor is the join:

```

Transaction.merchant_name "Ferguson Enterprises" (Merchant — read-only, no FK)

│

▼ auto-match by name

Accounting Vendor "Ferguson Enterprises"

▲

│ accounting_vendor_remote_id (explicit FK)

Vendor (Bill Pay) "Ferguson Enterprises" — has bank account on file

│

▼ 1:N

Bill ──────────► ERP export

```

Both the card transaction and the bill payment land on the same GL vendor entry, unifying the payee in the general ledger even though the two source records never reference each other.

Matching mechanics:

- **Merchant → Accounting Vendor**: name-based auto-match, with conditional auto-create defaulting ON and disable-able. Supported for QuickBooks, QuickBooks Desktop, NetSuite REST, Xero.

- **Vendor → Accounting Vendor**: explicit, via `PATCH /vendors/{id}` setting `accounting_vendor_remote_id`. Also settable in UI or by CSV import.

- **Accounting Vendor → Vendor**: opt-in auto-create, off by default, with two modes — import all, or only those with bills in the ERP.

- **Merchant ↔ Vendor**: unified in the UI only; explicitly "not available through the Developer API."

`[recommendation]` This is a genuinely hard problem and Ramp's answer is pragmatic rather than elegant. If you are starting clean, consider a fourth entity — a **Counterparty** aggregate that owns identity resolution and to which Merchant, Vendor, and Accounting Vendor all attach as projections. Ramp's model leaks the absence of that abstraction (hence the UI-only unified view). But be honest about the cost: identity resolution across normalized merchant strings, DBA names, and ERP vendor lists is an ML problem, not a schema problem. Ramp has a whole engineering post on fixing merchant matches with AI. Do not expect a join to solve it.

## State machines

### Sync status — shared across five object types

Published as applying uniformly to bills, transactions, reimbursements, transfers, and cashbacks:

```

NOT_SYNC_READY → SYNC_READY → SYNCED

```

Readiness conditions differ per object:

| Object | Ready when |

|---|---|

| Bills | Approved (or created, per settings) and not yet synced |

| Bill payments | Bill fully paid (`status: PAID`) |

| Transfers, cashbacks | Automatic |

| Transactions, reimbursements | User marks ready in UI |

Bills are **two-phase**, tracked jointly by `sync_ready` + `sync_status` + bill `status`:

| `sync_status` | `status` | Posts |

|---|---|---|

| `NOT_SYNCED` | `OPEN` | `BILL_SYNC` only |

| `NOT_SYNCED` | `PAID` | `BILL_SYNC`, then `BILL_PAYMENT_SYNC` |

| `BILL_SYNCED` | — | `BILL_PAYMENT_SYNC` only |

A single shared sync state machine across five heterogeneous objects is a strong design decision. It means the ERP connector is written once, against one interface, rather than five times. `[recommendation]` Adopt this — define a `SyncableFinancialObject` interface and make everything postable to the GL implement it.

### Bill status

```

DRAFT → PENDING APPROVAL → APPROVED → PAID

```

Notable: bills created via API are automatically approved and enter at `APPROVED`. Draft bills can be created and updated via API but **can only be approved in the dashboard** — approval is deliberately not API-exposed. `[inferred]` That is an anti-fraud decision, not a missing feature. If an API token could approve a bill, a compromised token could move money to an attacker-controlled vendor.

### Reimbursement status

```

DRAFT → PENDING → APPROVED → REIMBURSED

```

Plus edge states: `REJECTED`, `CANCELED`, `FAILED_REIMBURSEMENT`, and payment-specific `AWAITING_PAYMENT`, `PROCESSING`, `REIMBURSED_VIA_PUSH`.

Direction enum: `BUSINESS_TO_USER` (default) and `USER_TO_BUSINESS`.

### Application status

```

STARTED → IN_REVIEW → { FOLLOW_UPS_REQUIRED | APPROVED | REJECTED | WITHDRAWN }

```

One active financing application per business, so `GET` returns a single object rather than a list.

## Money representation

Published rules, and these are non-negotiable invariants:

- **Integers in the smallest currency denomination.** Multiply major units by 10^D where D is the currency's decimal places. USD/EUR/GBP D=2, JPY D=0.

- Some fields are an object of `{value, currency}`; some allow negatives for refunds and credits.

- ISO 4217 currency codes, plus stablecoin identifiers such as `USDC` for eligible Bill Pay payments. Presence of a currency in a schema does not mean every rail supports it.

- Banking balance history uses `amount` + `currency_code`, with a read-only `minor_unit_conversion_rate` that can be null. Divide `amount` by the rate to get major units when present. Never send the conversion rate on requests.

- One documented exception: AI Usage reports `reported_cost.amount` as a **decimal string** rather than a minor-unit integer.

- Dates and datetimes are ISO 8601 strings; UTC assumed absent an offset.

### Multi-currency reimbursement fields

This is the clearest published example of how to model cross-currency correctly:

| Field | Meaning |

|---|---|

| `line_items[].amount` | Original amount per expense line item |

| `original_reimbursement_amount` | Original total expense amount |

| `amount` + `currency` | Total the business pays |

| `payee_amount` | Amount and currency the employee receives |

A PLN 1,940 expense keeps `line_items[].amount` and `original_reimbursement_amount` in PLN, while `amount`, `currency`, and `payee_amount` reflect the USD paid out.

There is an explicit warning: **do not** use `line_items[].converted_amount` to determine a reimbursement line item's paid amount — it is not populated for reimbursement line items and can be null.

`[recommendation]` The lesson generalizes. A cross-currency money movement has at least four amounts (original, settled, paid, received) and they are not derivable from one another after the fact because the FX rate at authorization differs from the rate at settlement. Store all of them. Storing one amount plus a rate is a bug you will discover during your first audit.

## Schema sketch

Illustrative Postgres DDL for the core spine. `[recommendation]` — this is my design, not Ramp's published schema.

```sql

-- Tenancy

CREATE TABLE business (

id uuid PRIMARY KEY,

legal_name text NOT NULL,

status text NOT NULL, -- prospect|active|suspended|closed

created_at timestamptz NOT NULL DEFAULT now()

);

CREATE TABLE entity (

id uuid PRIMARY KEY,

business_id uuid NOT NULL REFERENCES business,

legal_name text NOT NULL,

country char(2) NOT NULL,

base_currency char(3) NOT NULL,

UNIQUE (business_id, legal_name)

);

CREATE TABLE location (

id uuid PRIMARY KEY,

business_id uuid NOT NULL REFERENCES business,

entity_id uuid NOT NULL REFERENCES entity, -- entity derives through here

name text NOT NULL

);

CREATE TABLE app_user (

id uuid PRIMARY KEY,

business_id uuid NOT NULL REFERENCES business,

location_id uuid REFERENCES location,

department_id uuid REFERENCES department,

direct_manager_id uuid REFERENCES app_user,

role text NOT NULL, -- BUSINESS_USER|BUSINESS_ADMIN|...

status text NOT NULL, -- USER_DRAFT|INVITE_PENDING|...

email citext NOT NULL,

UNIQUE (business_id, email)

);

-- Spend controls

CREATE TABLE spend_program (

id uuid PRIMARY KEY,

business_id uuid NOT NULL REFERENCES business,

version int NOT NULL DEFAULT 1,

display_name text NOT NULL,

description text,

is_shareable boolean NOT NULL DEFAULT false,

permitted_spend_types jsonb NOT NULL, -- {primary_card_enabled, reimbursements_enabled}

spending_restrictions jsonb NOT NULL, -- {limit:{amount,currency}, interval, allowed_categories:[int]}

UNIQUE (business_id, display_name, version)

);

CREATE TABLE fund (

id uuid PRIMARY KEY,

business_id uuid NOT NULL REFERENCES business,

entity_id uuid NOT NULL REFERENCES entity,

spend_program_id uuid REFERENCES spend_program, -- null = ad-hoc fund

program_version int, -- pinned at mint time

display_name text NOT NULL,

status text NOT NULL, -- ACTIVE|SUSPENDED|TERMINATED

-- denormalized from program at mint time; immutable thereafter

limit_amount bigint NOT NULL, -- minor units

limit_currency char(3) NOT NULL,

interval text NOT NULL, -- DAILY|MONTHLY|ANNUAL|TOTAL

allowed_categories int[],

allowed_merchants uuid[],

allowed_countries char(2)[],

created_at timestamptz NOT NULL DEFAULT now(),

terminated_at timestamptz

);

CREATE TABLE fund_member (

fund_id uuid NOT NULL REFERENCES fund,

user_id uuid NOT NULL REFERENCES app_user,

PRIMARY KEY (fund_id, user_id)

);

-- Cards

CREATE TABLE card (

id uuid PRIMARY KEY,

business_id uuid NOT NULL REFERENCES business,

fund_id uuid NOT NULL REFERENCES fund,

cardholder_id uuid NOT NULL REFERENCES app_user,

form_factor text NOT NULL, -- PHYSICAL|VIRTUAL|AGENT

is_primary boolean NOT NULL DEFAULT false,

state text NOT NULL, -- ACTIVE|LOCKED|TERMINATED

last_four char(4) NOT NULL,

exp_month smallint NOT NULL,

exp_year smallint NOT NULL,

processor_ref text NOT NULL, -- opaque id at the issuer processor

processor_name text NOT NULL, -- which processor issued it

created_at timestamptz NOT NULL DEFAULT now()

);

-- No PAN column. Ever. See 09-compliance-and-risk.md.

-- Primary card fan-out to multiple funds

CREATE TABLE card_fund_link (

card_id uuid NOT NULL REFERENCES card,

fund_id uuid NOT NULL REFERENCES fund,

priority smallint NOT NULL, -- routing order for auto-selection

PRIMARY KEY (card_id, fund_id)

);

```

Two things to notice in that sketch. `card` has no PAN column — the pan lives only at the processor, retrieved transiently through a vault API or rendered into an iframe. And `fund` denormalizes its restrictions from the program at mint time rather than joining through, because the authorization path cannot afford a join to a table an admin might be editing.

