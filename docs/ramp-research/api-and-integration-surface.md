# 08 — API and Integration Surface

Ramp's public API is well-specified, and the specification is worth copying almost wholesale because the design decisions embedded in it were paid for with production incidents.

## Documentation infrastructure

Worth noting before the API itself. Ramp publishes machine-readable documentation specifically for LLM consumption:

| Path | Contents |

|---|---|

| `/llms.txt` | Index of everything |

| `/llms-guides.txt` | All guides combined |

| `/llms-guides/<slug>.txt` | Individual guide as plain text |

| `/llms-api.txt` | Generated endpoint and schema reference |

| `/llms-full.txt` | Guides + API reference combined |

| `/openapi/developer-api.json` | Canonical OpenAPI spec |

Their own instruction to agents is explicit: don't render `docs.ramp.com` pages, they are "JavaScript shells" — route guide URLs to the matching `/llms-guides/` file and API reference URLs to `/llms-api.txt`.

They also ship **Developer Assist**, an AI helper built into the docs, and a **Developer MCP** server so agents can query the docs directly.

`[recommendation]` Do this. It costs a build step and it means every AI coding assistant your integrators use can read your API correctly instead of hallucinating endpoints from a JS-rendered page. In 2026 your documentation has two audiences and one of them cannot execute JavaScript.

## Authentication

Three OAuth 2.0 grant types, at `/developer/v1/token`, authenticated with client ID/secret via HTTP Basic (some clients send credentials in the form body).

| Grant | For | User consent |

|---|---|---|

| **Client Credentials** | Internal integrations, server-to-server | None |

| **Authorization Code** | Third-party apps, public integrations | Required |

| **Refresh Token** | Renewing after Authorization Code | None |

### Token lifetimes

| Token type | Lifetime |

|---|---|

| Client Credentials | **10 days** (864,000 s). Not refreshable — request a new one. |

| Authorization Code / Refresh | **1 hour** (3,600 s) default, varies by app |

Actual lifetime is always in `expires_in`. `refresh_token_expires_in` appears only when a refresh token is returned and the app has a configured refresh lifetime. **Refreshing an access token does not extend the refresh token's own expiry.**

Token prefixes: `ramp_business_tok_`, `ramp_user_tok_`, `ramp_business_jwt_`, `ramp_user_jwt_`.

`[recommendation]` Prefixed tokens are a small, high-value detail. They make secret-scanning tools (GitHub, TruffleHog, gitleaks) able to detect your credentials in public repos and alert you. Adopt a distinctive, greppable prefix per token class. The prefix also tells your own logs what kind of principal is acting without a database lookup.

The 10-day client-credentials lifetime is a deliberate middle ground — long enough that a cron job does not need refresh-token machinery, short enough that a leaked token expires. `[recommendation]` Reasonable, but consider shorter with mandatory refresh for anything with write scopes.

### Authorization Code specifics

- HTTPS redirect URIs required.

- `state` parameter must be cryptographically random and verified.

- Authorization codes are short-lived — **10 minutes**.

- Approval is "typically limited to Admin and Business Owner users." A regular employee cannot grant a third-party app access to company financial data.

- Revocation for both flows: `POST /developer/v1/token/revoke`.

### Environment isolation

Sandbox and production require **separate app registrations**. Tokens are valid only in the environment that issued them. Sandbox is a separate environment with its own base URL and credentials — explicitly "not a mode within the production API."

`[recommendation]` This is the right call and the opposite of what many fintech APIs do (a test-mode flag on the same account). Separate environments make it structurally impossible to leak a test token into production or to accidentally move real money from a test suite. Ramp pre-populates sandbox businesses with sample transactions, cards, users, departments, and reimbursements — do this too, because an empty sandbox means every integrator's first hour is spent manufacturing fixtures.

### Multi-tenant reality

For a third-party app serving many customers, **each customer's Admin or Business Owner must individually complete the Authorization Code flow.** There is no bulk or partner-level authorization, and no cross-tenant token sharing. Correct, but it means partner onboarding is per-customer manual work — plan the UX for it.

## Scopes

The full published list, which doubles as the resource inventory (discussed in `02-domain-model.md`):

```

accounting:read/write applications:read/write bank_accounts:read/write

bills:read/write budgets:read business:read

cards:read cards:write cards:read_vault

cashbacks:read custom_records:read/write departments:read/write

entities:read funds:read/write incorporation:read/write

item_receipts:read/write limits:write locations:read/write

memos:read/write merchants:read purchase_orders:read/write

receipt_integrations:r/w receipts:read/write reimbursements:read/write

spend_programs:read/write statements:read tasks:read

transactions:read/write transfers:read treasury:read

users:read/write vendors:read/write blank_canvas:write

openid offline_access

```

Design notes:

- **`resource:permission` naming throughout**, with only the OIDC scopes (`openid`, `offline_access`) deviating. Consistent, predictable, self-documenting.

- **`cards:read_vault` is separate from `cards:read`.** PAN access is its own scope, not a level of card access — so an integration can read card metadata without ever being able to request a PAN. Separating the dangerous capability into its own scope is the single most important thing in this list.

- Ramp's documented guidance is to "start with read-only scopes and add write permissions as needed."

- If `scope` is omitted on a client-credentials request, Ramp issues a token with **no scopes**. Fail closed. A missing scope parameter is not "give me everything."

- Some scopes are read-only with no write counterpart: `merchants:read` (network-owned data), `treasury:read`, `statements:read`, `cashbacks:read`, `transfers:read`, `budgets:read`, `tasks:read`, `entities:read`. The absence of a write scope is a security decision expressed in the scope list.

- `cards:read_vault` additionally requires **production approval** — a support ticket triggers review of use case, security controls, and PCI handling. Sandbox is open to all.

`[recommendation]` Copy all of it, especially: dangerous capabilities get their own scope, and the most dangerous ones get a human approval gate on top of the scope.

## Rate limits and timeouts

| Property | Value |

|---|---|

| Rate limit | **200 requests per 10-second rolling window**, per source IP |

| Exceeded | `429 Too Many Requests` |

| Request timeout | **60 seconds** → `504 Gateway Timeout` |

| Max page size | **100 items** |

| Theoretical max throughput | ~120,000 records/minute |

| Recommended retry | Exponential backoff (1s, 2s, 4s) |

| Raising limits | Developer API support ticket with documented usage |

The window is genuinely rolling: 200 requests at 10:00:00 stop counting at approximately 10:00:10.

`[inferred]` Rate limiting **per source IP** rather than per token is unusual and probably a mistake worth avoiding. It means multiple integrations behind one NAT gateway share a budget, and a single misbehaving tenant on shared infrastructure degrades everyone. `[recommendation]` Rate limit per **token or per business**, with a separate global IP-level limit as abuse protection only. Ramp's own engineering blog has a post on rate limiting with Redis; use that pattern but pick the right key.

## Pagination

Cursor pagination on list endpoints, max 100 items per page.

`[recommendation]` Cursor over offset, always, for financial data. Offset pagination over a table receiving concurrent inserts silently skips and duplicates rows, which in an accounting export means a missing or double-posted journal entry. This is not a performance preference; it is a correctness requirement.

## Incremental sync — the design mistake to avoid

Covered in detail in `06-accounting-erp-sync.md`, restated here because it is the most instructive flaw in the whole API.

| Endpoint | Incremental param | Gap |

|---|---|---|

| `GET /transactions` | `synced_after` | Only accounting-sync commits. Misses new, changed, and late-posted transactions. |

| `GET /bills` | `from_created_at` | New records only. **No updated-at filter.** Status changes need webhooks or full re-pulls. |

| `GET /purchase-orders` | none | Webhooks or full re-pulls only. |

Ramp's own explicit warning: *"Do not treat `synced_after` as a replacement for an updated-at filter."*

`[recommendation]` **Ship `updated_at` cursor pagination on every list endpoint on day one.** It is nearly free to design in and effectively impossible to retrofit — retrofitting means backfilling a column on a table with hundreds of millions of rows, then migrating every integrator. The consequence of not doing it is that your partners either re-pull everything on a schedule or trust an event stream you have told them may arrive out of order. Neither is acceptable, and both are permanent.

## Idempotency

Notable for its near-absence. The only place an explicit `idempotency_key` appears in Ramp's published API is `POST /accounting/syncs`, where retries reuse the key for server-side dedup.

`[inferred]` The rationale, as discussed in `06`: marking objects synced is the one operation where a duplicate silently corrupts state the caller cannot detect. Elsewhere, either the operation is naturally idempotent, or a uniqueness constraint catches it, or the operation simply is not exposed (bill approval, vendor creation, bank account creation).

`[recommendation]` Do better. Accept an `Idempotency-Key` header on **every** POST and PATCH, store the key with the response, and replay the stored response on a repeat. Every integrator's network will time out mid-request eventually, and without idempotency their only options are to retry (and risk a duplicate) or not retry (and risk a lost write). For anything that moves money, neither is a choice you should force on them.

## Webhooks

The best-specified part of Ramp's API. Copy it closely.

### Complete event catalog

**Applications** — `applications.status_updated`

**Bills** — `bills.approved`, `bills.archived`, `bills.created`, `bills.paid`, `bills.ready_to_sync`, `bills.rejected`, `bills.updated`

**Entities** — `entities.created`

**Item Receipts** — `item_receipts.created`

**Purchase Orders** — `purchase_orders.archived`, `purchase_orders.created`, `purchase_orders.updated`

**Reimbursements** — `reimbursements.batch_payment_reimbursed`, `reimbursements.ready_for_review`, `reimbursements.ready_to_sync`, `reimbursements.sync_requested`

**Spend Requests** — `spend_requests.comment_created`, `spend_requests.created`

**Transactions** — `transactions.all_requirements_met_and_approved_changed`, `transactions.authorized`, `transactions.body_coding_updated`, `transactions.cleared`, `transactions.declined`, `transactions.ready_for_review`, `transactions.ready_to_sync`, `transactions.receipt_added`, `transactions.sync_requested`, `transactions.synced`

**Unified Requests** — `unified_requests.created`, `unified_requests.external_approval_request`, `unified_requests.external_approval_request_reset`, `unified_requests.modified`, `unified_requests.node_advanced`, `unified_requests.override_approved`, `unified_requests.updated`

**Users** — `users.invite_accepted`

**Vendor Agreements** — `vendor_agreements.archived`, `vendor_agreements.created`, `vendor_agreements.deleted`, `vendor_agreements.document_added`, `vendor_agreements.renewal_milestone`, `vendor_agreements.updated`

**Vendors** — `vendors.activated`, `vendors.approved`, `vendors.updated`

**System** — `tests.test_event` (mock delivery only), `webhooks.verification` (endpoint verification only)

Two things to read out of this list. First, `transactions.authorized` and `transactions.declined` are exposed — meaning the auth stream is observable, which is what makes real-time spend dashboards and instant Slack notifications possible. Second, the `unified_requests.*` events (`node_advanced`, `external_approval_request`, `override_approved`) are the workflow engine from `03-architecture.md` surfacing as events. Approval workflow state changes are externally observable, which is how "Blank Canvas" external approvals work at all.

### Envelope

Every payload contains `id`, `type`, `created_at` (ISO 8601), `business_id`, and `object` (the affected resource ID plus event-specific metadata).

Note what is **not** in the envelope: the full resource. You get an ID and you re-fetch. That is the right choice — a full-resource payload becomes stale in flight, and stale financial data acted upon is worse than a second HTTP call.

Business-event deliveries also carry `X-Ramp-Webhook-ID` matching the payload `id`; verification requests omit this header.

### Verification handshake

- Subscriptions start in `pending_verification` and receive **no events** until verified.

- Ramp sends a challenge; the endpoint returns 2xx; the challenge is then submitted to a verification endpoint which returns `{"success": true}`.

`[recommendation]` The `pending_verification` state is what prevents your webhook sender from being turned into a DDoS amplifier pointed at a third party. Without it, anyone can register `https://victim.example.com` and have you flood it. This is a security control, not a convenience.

### Signing

- `X-Ramp-Signature` header: **HMAC-SHA256 of the raw body**, signed with a per-subscription secret returned at creation.

- Documented emphasis: verify **"the exact raw request bytes before parsing or reserializing the JSON."** Re-serializing via `JSON.stringify(req.body)` invalidates the signature.

That warning exists because everyone hits it. Express and most frameworks parse JSON before your handler runs, and re-stringifying produces different bytes (key order, whitespace, number formatting). You must capture the raw buffer.

Per-subscription secrets, not one global secret, mean rotating or compromising one endpoint does not affect the others.

### Retries

| Status | Behavior |

|---|---|

| 2xx | Success, no retries |

| 3xx, 4xx except 429 | **Immediate failure, no retries** |

| 429, 5xx, timeouts | Up to **10 total attempts**, exponential backoff |

- First retry delay 0–2 s, scaling to a **60 s maximum**, using **full jitter**.

- Endpoints must respond within **10 seconds**.

- Retries reuse the same event `id`, enabling idempotency.

- **Events may arrive out of order** — check timestamps and re-fetch current state rather than trusting order.

Three details worth calling out. Not retrying 4xx is correct: a 404 or 401 means the endpoint is misconfigured and retrying ten times will not fix it, it will just delay the operator noticing. **Full jitter** (versus fixed or decorrelated backoff) is the AWS-recommended algorithm and materially reduces thundering-herd on recovery — Ramp uses it, so should you. And the explicit out-of-order warning is honest engineering: an at-least-once system with retries cannot guarantee order, and pretending otherwise pushes a subtle bug onto every consumer.

### Custom headers

Up to five `additional_headers` per subscription, 100-char names / 1,000-char values. Reserved prefixes and names, case-insensitive: `Host`, `User-Agent`, `X-Forwarded*`, `X-Real*`, `X-Original*`.

Small but useful — lets an integrator route your webhooks through their own gateway with an auth header without you building bespoke support.

### Subscription management

- `POST /developer/v1/webhooks` — create. **Requires read scopes matching the selected events.** You cannot subscribe to bill events without `bills:read`.

- `POST /developer/v1/webhooks/mock-webhook-event` — fire a mock event to all matching active subscriptions for the token's business. Requires `event_type`, `object_id` (a valid resource UUID), `object_metadata`. Returns 201 with the generated payload.

- **Updating an endpoint URL requires delete → create → re-verify.** No in-place URL change — which is a deliberate control, since in-place URL mutation would bypass the verification handshake.

- Multi-customer subscriptions use the same `/webhooks` endpoints, with `business_id` in payloads identifying the owning business.

`[recommendation]` The mock-event endpoint is a genuinely thoughtful integrator-experience feature. Without it, testing a webhook consumer requires manufacturing real business events. Ship it.

## Async operations

Long-running work returns a task, not a result:

- `POST /developer/v1/users/deferred` → task id

- `GET /developer/v1/users/deferred/status/{task_id}` → `STARTED` | `IN_PROGRESS` | `ERROR` | `SUCCESS`

- On success, `data.user_id` holds the created UUID

- Most tasks finish in under 5 seconds

- `tasks:read` scope

`[recommendation]` The pattern is right: operations that fan out to external providers return a task handle rather than blocking. But polling is a weak completion mechanism. Emit a webhook on task completion too, so integrators can choose. Ramp has `users.invite_accepted` but no generic `tasks.completed`.

## Error handling

Published error codes follow a `DEVELOPER_NNNN` / `CUSTOM_RECORDS_NNNN` convention:

| Code | Meaning |

|---|---|

| `DEVELOPER_7001` | Payload validation failure |

| `DEVELOPER_7122` | Bad field `remote_id` |

| `DEVELOPER_7123` | Bad or inactive option `remote_id` |

| `CUSTOM_RECORDS_7003` | Rows in batch have different result columns |

`[recommendation]` Stable, specific, documented, machine-readable error codes are the difference between an integrator branching on your code and an integrator regex-matching your error message. The second one breaks every time you improve your copy. Namespace-prefixed numeric codes with a published table is the right form.

## Distribution surface

- **App Center** — third parties develop, publish, and market integrations on Ramp.

- **Technology partnership** application flow.

- **Conferma onboarding** — a virtual-card/travel-payments partner integration with its own documented onboarding request.

- 200+ to 1,000+ integrations depending on counting method.

`[inferred]` The App Center is strategically significant beyond integrations. Every partner-built connector is distribution Ramp does not pay for, and it deepens switching costs — a customer with six App Center integrations wired into their close process is far harder to displace than one with a card program. If you are cloning, the platform surface is not a phase-9 nice-to-have; it is part of the moat.