# 06 — Accounting and ERP Synchronization

The unglamorous module that determines whether a finance team adopts you. Ramp's documentation is unusually complete here, so most of this file is sourced fact rather than inference.

## The two-way flow

```

ERP / integrator ──── chart of accounts ────► RAMP

(GL accounts, custom fields, options, vendors, entities)

so employees have valid values to code spend against

RAMP ──── ready-to-sync objects ────► integrator ────► ERP

(transactions, bills, bill payments, reimbursements, transfers, cashbacks)

then marked synced

```

Ramp ships native connectors (QuickBooks, QuickBooks Desktop, Xero, NetSuite, Sage Intacct, Workday, Oracle) **and** exposes a generic accounting API so third parties can connect any ERP. The generic path uses a `remote_provider_name` field which is "what your customer sees in Ramp when picking providers."

Constraint: **one active connection per customer**, direct or API-based. Not both.

## Chart-of-accounts ingestion

Five uploadable object types:

| Object | Endpoint |

|---|---|

| GL accounts | `POST /accounting/accounts` |

| Custom fields | `POST /accounting/fields` |

| Custom field options | `POST /accounting/field-options` |

| Accounting vendors | `POST /accounting/vendors` |

| Entities (subsidiaries) | `POST /accounting/entities` |

Plus tax codes, tax code options, tax rates, inventory items, inventory item options, and Ramp-only fields (`/accounting/ramp-fields`, `/accounting/ramp-field-options`) — dimensions that exist in Ramp for internal reporting but do not correspond to anything in the ERP.

Batch limit: **500 items per request, all-or-nothing per batch.**

Ordering requirement: **create the field first, then upload its options using the returned `ramp_id`.** Options reference their parent field by Ramp's ID, not the ERP's.

Custom fields import ERP classifications like Department, Cost Center, or Location. Note the collision: Ramp has native `department` and `location` entities for org structure *and* imports the ERP's department and location dimensions as custom fields. They are not the same thing and must not be conflated — one governs who a person reports to, the other governs which GL bucket a dollar lands in.

### Entity scoping

Multi-entity is controlled by `settings.entity_selection_enabled`, scoped via `entity_id` on reads and `entity_remote_ids` on uploaded options.

Entity scoping is supported on GL accounts, custom field options, accounting vendors, tax code options, and inventory item options. So a subsidiary in Germany sees only the GL accounts and cost centers valid for that entity.

### Lifecycle: delete versus hide

Two distinct soft-removal mechanisms, and the distinction matters:

| Operation | Effect | Reversal |

|---|---|---|

| **Delete** | `DELETE` sets `is_active: false` | `PATCH { "reactivate": true }` |

| **Hide** (field options only) | `PATCH { "visibility": "HIDDEN" }` | `PATCH { "visibility": "VISIBLE" }` |

The published rationale for hide: it "preserves sync eligibility for historical values." A closed cost center should not appear in this year's dropdown, but last year's transactions coded to it must still export correctly.

`[recommendation]` This is a genuinely good pattern worth generalizing. Any reference data that historical records point at needs three states, not two: **active** (selectable, syncable), **hidden** (not selectable, still syncable), **inactive** (neither). A two-state active/deleted model will break your historical exports the first time a customer reorganizes their chart of accounts.

There are no hard deletes anywhere in this model.

## Coding

Coding writes go through `POST /accounting/codings` with:

- `object_type: "TRANSACTION"`

- `object_id`

- `accounting_coding_selections` — referencing Ramp `ramp_id` values, **not ERP remote IDs**

- `free_form_text` for free-form fields

The `ramp_id` versus `remote_id` distinction runs through the whole API and is a frequent source of bugs. Uploads to Ramp carry the ERP's `remote_id`. Reads and coding selections use Ramp's `ramp_id`. You need a durable bidirectional map, and it must survive the ERP changing a remote ID (which QuickBooks Desktop will do to you).

## Field Option Filter Rules

A beta feature, and the most sophisticated part of the accounting model. It restricts which field options an employee sees based on their prior selections — Project → Task, or Project + Task → Cost Type.

Structure:

- **Target field option** — the option conditionally enabled

- **Required selections** — the trigger field + option combinations

Logic, published verbatim: *"Multiple `required_selections` within a single rule use AND logic... Multiple rules for the same target option use OR logic."*

That is disjunctive normal form. Each rule is a conjunction; the rule set is a disjunction over rules. Any boolean condition can be expressed, and evaluation is a simple two-level loop with no expression parser. `[recommendation]` Adopt this exact shape. It is the sweet spot between a single flat rule list (not expressive enough) and a general expression language (which you then have to parse, validate, version, and explain to accountants).

Endpoints: `GET`/`POST`/`DELETE /accounting/field-option-filter-rules`, referencing fields and options by ERP `remote_id`. Bulk create and bulk delete are both `POST`.

Lifecycle interaction: soft-deleting a field option **suspends** rather than deletes its rules; reactivating the option auto-resumes them. Again, no destructive cascade.

Published error codes:

| Code | Meaning |

|---|---|

| `DEVELOPER_7122` | Bad field `remote_id` |

| `DEVELOPER_7123` | Bad or inactive option `remote_id` |

| `DEVELOPER_7001` | Payload validation failure |

## Approver matrix tables

Ramp implements dimension-based approval routing through **matrix tables** built on the custom records API — mapping accounting dimensions (projects, departments, cost centers) to approvers. The documented example is a "Project Approver Matrix."

Mechanics:

- `accounting_field_ramp_id` references the accounting field option

- Column relationship types: `many_to_many` versus `many_to_one`

- Row upserts via `PUT`, with identifiers accepted as Ramp UUID, email, `code`, or `name`

- Error `CUSTOM_RECORDS_7003` — "Rows in batch have different result columns"

`[inferred]` This is a clever piece of leverage. Rather than building a bespoke "who approves project X" feature, Ramp exposed a generic key-value-matrix primitive (`custom_records`) and expressed approval routing as data in it. The workflow engine described in `03-architecture.md` then references the matrix as registered configuration. One primitive, many routing policies, no engine changes.

`[recommendation]` Worth copying, but note the accepted-identifier flexibility (UUID *or* email *or* code *or* name) is a real usability decision — finance teams maintain these in spreadsheets and will not have your UUIDs. Accept natural keys on write and resolve them server-side.

## The sync protocol

### Shared sync state

One state machine across bills, transactions, reimbursements, transfers, and cashbacks:

```

NOT_SYNC_READY → SYNC_READY → SYNCED

```

Readiness conditions:

| Object | Ready when |

|---|---|

| Bills | Approved (or created, per settings), not yet synced |

| Bill payments | Bill fully paid (`status: PAID`) |

| Transfers, cashbacks | Automatic |

| Transactions, reimbursements | User marks ready in the Ramp UI |

Note the split: system-originated movements are automatically ready; human-originated spend requires a human to confirm the coding is right before it hits the general ledger. That is the correct division of trust.

### Bills are two-phase

Because a bill and its payment are separate GL events (the liability, then its discharge), bills sync twice. Tracked jointly by `sync_ready` + `sync_status` + bill `status`:

| `sync_status` | `status` | Post |

|---|---|---|

| `NOT_SYNCED` | `OPEN` | `BILL_SYNC` only |

| `NOT_SYNCED` | `PAID` | `BILL_SYNC`, then `BILL_PAYMENT_SYNC` |

| `BILL_SYNCED` | — | `BILL_PAYMENT_SYNC` only |

### The sync round trip

1. **Push the coding surface** — upload GL accounts, fields, options, vendors, entities.

2. **Fetch ready objects** — `GET /transactions?sync_status=SYNC_READY`, `GET /bills?sync_ready=true`.

3. **Post to the ERP** — the integrator writes into the remote system.

4. **Mark synced** — `POST /accounting/syncs` with:

- `idempotency_key`

- `sync_type` (`TRANSACTION_SYNC`, `BILL_SYNC`, `BILL_PAYMENT_SYNC`, ...)

- `successful_syncs` **or** `failed_syncs`

5. **Detect new work** — polling or webhooks.

6. **Surface errors** — `failed_syncs` appear in Ramp's UI as "Export Errors."

Batch limit: **5,000 successful or 5,000 failed syncs per call.** Retries reuse the same `idempotency_key` for server-side dedup.

This is the **only** place in Ramp's published API where an explicit `idempotency_key` appears. `[inferred]` That is not an accident: marking objects synced is the one operation where a duplicate call silently corrupts state in a way the caller cannot detect (you would double-post to the customer's general ledger). Everywhere else, duplicates are either naturally idempotent or caught by uniqueness constraints.

### Error taxonomy

`failed_syncs` are categorized three ways:

1. **User-actionable** — missing GL account, invalid coding. The customer must fix it.

2. **Transient** — ERP timeout, rate limit. Retry.

3. **Integrator support needed** — a bug in the connector.

`[recommendation]` This taxonomy is the difference between a support-ticket firehose and a self-service product. Every sync failure must be classified before it is displayed, because "Export Error: 400 Bad Request" generates a ticket and "Missing GL account for category Software — assign one here" does not.

### Detection: polling versus webhooks

Published polling cadence guidance:

- Weekdays: every 1–4 hours

- Weekends: every 12 hours

- Real-time needs: use webhooks (`transactions.ready_to_sync`, `bills.ready_to_sync`, `reimbursements.ready_to_sync`)

**Sync Button** (Alpha) lets the customer trigger a sync on demand via `*.sync_requested` webhooks, with a **5-minute response window** for the integrator. Ramp's guidance is to only add the Sync Button "once round-trips are fast enough" — the feature is gated on the integrator's own latency.

### The incremental-sync trap

This is the most operationally important warning in Ramp's docs, and it generalizes to any API you design.

| Endpoint | Incremental param | Limitation |

|---|---|---|

| `GET /transactions` | `synced_after` | "Returns transactions with an accounting sync commit at or after the specified time." **Does not return every new, changed, or late-posted transaction.** |

| `GET /bills` | `from_created_at` | Catches new records only. **No updated-at filter exists.** Status changes require webhooks or full re-pulls. |

| `GET /purchase-orders` | none | Updates require webhooks or periodic full re-pulls. |

Explicit caution: **"Do not treat `synced_after` as a replacement for an updated-at filter."**

`[recommendation]` The lesson for your own API: **ship a monotonic `updated_at` cursor on every list endpoint from day one.** It is nearly free at design time and effectively impossible to retrofit, because retrofitting means backfilling a column on a table with hundreds of millions of rows and then convincing every integrator to migrate. Ramp's integrators are stuck doing full re-pulls or trusting an event stream that the docs themselves say may arrive out of order. That is a permanent tax on every partner integration.

## Build guidance

`[recommendation]`

**Connector order:** QuickBooks Online, then Xero, then NetSuite, then Sage Intacct. QBO and Xero cover the SMB volume and have modern REST APIs. NetSuite is where the enterprise revenue is and where the pain is — SuiteQL, governance limits, and per-customer customization mean NetSuite is not one integration but one integration per customer. Budget accordingly. QuickBooks Desktop, if you must, is a Windows-agent-and-file-drop integration; treat it as a separate product.

**Build the generic accounting API before the second native connector.** Ramp's model — one generic API that native connectors also consume — means the connector team and the partner ecosystem exercise the same code path. If your native connectors reach into internal services while partners get a thinner public API, the public one will be permanently second-class.

**Test with a real accountant, at month-end.** The whole module's value is measured in days-to-close. Every design question — whether hidden options stay syncable, whether errors are classified, whether the matrix accepts emails — has an obvious answer if you have watched someone close books and no obvious answer if you have not.