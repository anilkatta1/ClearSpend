# Appendix — ClearSpend Code Review and Ramp Blueprint Alignment

> **Canonical cross-functional assessment:** [Product/Ramp alignment assessment](product/ramp-alignment-assessment.md). This appendix supplies the detailed code, security, reliability, and documentation evidence behind that assessment; it is not a competing product roadmap.

**Subject:** `ClearSpend-main/` (commit as of 2026-09-11)

**Measured against:** `research/ramp/` — the Ramp technical clone blueprint

**Review date:** 2026-09-11

**Method:** Full read of the backend (`services/backend/app`, ~1,400 LOC), frontend (`apps/web`), tests, CI, compose, evals, config, ADRs, and the two plan documents; cross-referenced against all twelve files of the Ramp dossier.

---

## 1. Framing: what "alignment" should mean here

ClearSpend is not an attempt to clone Ramp, and it should not be graded as one. `PRODUCT_ARCHITECTURE_AND_EXECUTION_PLAN.md:12` states this directly, and section 2 of that plan explicitly places card issuing, money movement, accounts payable, procurement, travel booking, ERP write-back, and company-wide fraud prediction outside the MVP boundary.

That means roughly 80% of the dossier is out of scope by design and correctly so:

- `04-card-issuing-and-authorization.md` — the sub-150ms authorization decisioner, hold lifecycle, clearing and settlement

- `05-payments-and-ap-rails.md` — ACH, wire, check, SWIFT, stablecoin

- `06-accounting-erp-sync.md` — chart-of-accounts ingestion, bidirectional sync, connectors

- Most of `09-compliance-and-risk.md` — KYB/KYC, PCI DSS scope, money transmission, underwriting

The dossier's own build plan supports this choice. `10-build-plan.md` failure mode #9 is "building eight shallow modules instead of two deep ones," and its closing argument is that depth beats breadth in this category because the product's job is to be trusted with the general ledger. Choosing one bounded workflow is the dossier's recommended posture, not a departure from it.

So the review measures ClearSpend against the parts of the dossier that genuinely bear on the chosen slice:

| Dossier file | Applies because |

|---|---|

| `02-domain-model.md` | Policy/spend-program versioning, state machines, money representation, multi-currency |

| `03-architecture.md` | Modular monolith, transactional outbox, audit boundary, reliability posture, shadow mode |

| `07-ai-ml-and-agents.md` | The governing rule for AI in a money system; evaluation separation; correction feedback loop |

| `08-api-and-integration-surface.md` | Idempotency, pagination, rate limits, error codes, incremental sync |

| `09-compliance-and-risk.md` | Tenant isolation, audit immutability, security baseline |

| `05-payments-and-ap-rails.md` | The reimbursement object and its state machine specifically |

**Overall verdict: alignment is high on principles and roughly 55% on mechanics.** The single most important architectural rule in the entire dossier is honored better than most production systems manage. Beneath that, there is one structural primitive missing, four genuine defects, and a documentation layer that describes capabilities the code does not yet have.

---

## 2. Where ClearSpend matches or beats the reference

### 2.1 The governing AI rule — honored precisely

`07-ai-ml-and-agents.md:138` states the rule the dossier says to write on the wall:

> The agent decides *what to look up* and *where to send the answer*. A calibrated model or a deterministic policy decides *the answer itself*.

ClearSpend implements this cleanly, and it is the strongest part of the codebase.

`domain.py:86` (`aggregate_recommendation`) partitions checks by `source` and allows only a `DETERMINISTIC` failure to produce `REJECT_RECOMMENDED`. The AI contributes exactly one advisory check (`ai.py:93`), and tracing the aggregation shows it can only ever *downgrade* an outcome:

- AI returns `PASS` → the recommendation is whatever the deterministic checks already implied

- AI returns `UNKNOWN` → `NEEDS_REVIEW`

- AI returns `FAIL` → falls through to `NEEDS_REVIEW` (an AI `FAIL` cannot produce a `REJECT`)

The AI has no tools at all, so `07:212`'s confused-deputy concern and `07:162`'s exposure-budget requirement are addressed by removing the capability rather than capping it — which is the stronger move at this stage of the product. `graph.py:31` additionally short-circuits the model entirely when a deterministic rule has already failed, so the expensive, adversarially-exposed step does not run when it cannot change the outcome. ADR 0002 records the reasoning.

`ai.py:80` validates that every cited policy section ID is a subset of the IDs supplied to the model, which is the concrete implementation of "cite only supplied IDs" and closes the most common citation-hallucination path.

### 2.2 Transactional outbox — the dossier's exact lesson, implemented

`03-architecture.md:71` recounts Ramp's Celery broker dropping roughly 7 tasks per 10,000, and the reason they built a Postgres-backed queue: with a separate broker you cannot atomically commit a database change and enqueue the work that depends on it. The dossier calls the outbox pattern "not optional" for a financial system.

ClearSpend implements it correctly:

- `main.py:294` writes the `OutboxEvent` in the same transaction as the expense state change

- Immediate enqueue is attempted after commit (`main.py:308`) and its failure is logged, not fatal

- `jobs.py:34` (`relay_outbox_batch`) continuously relays unpublished events with `FOR UPDATE SKIP LOCKED`, recovering any enqueue that failed

- Procrastinate is a Postgres-backed queue — structurally the same choice Ramp made, for the same reason

- A per-expense execution lock plus queueing lock plus the `UniqueConstraint("expense_id", "revision", "engine_version")` on `AssessmentAttempt` (`db.py:140`) gives at-least-once delivery with idempotent effect

ADR 0003 records this. This is a faithful, non-cargo-culted implementation of the dossier's highest-value reliability recommendation.

### 2.3 Policy versioning — better than the reference

`02-domain-model.md:111` describes Ramp's spend-program binding as fixed at mint time: funds inherit policy at creation and changing policy requires terminating and re-minting. The dossier praises the auditability and criticizes the rigidity, then recommends at `02:113`:

> Copy the template/instance split, but consider versioning the program and letting funds pin a version with an explicit migration operation. You get Ramp's auditability without its rigidity.

ClearSpend does exactly this, for policy rather than for funds:

- `PolicyVersion` with an `(organization_id, version)` unique constraint and a `DRAFT → PUBLISHED → SUPERSEDED` lifecycle (`main.py:188`)

- Published policies are immutable — `main.py:189` rejects re-publication with a domain conflict

- A canonical-JSON `content_hash` computed over sections and rules with sorted keys and stable separators (`main.py:197`), so the exact evaluated policy text is provable after the fact

- Every claim pins `policy_version_id` at submit (`main.py:273`), and the worker reads rules through that pin (`services.py:78`)

This is a genuine improvement on the reference model, and it is the single most defensible thing about the product from a finance-team trust standpoint.

### 2.4 Audit trail — exceeds the published Ramp model

`09-compliance-and-risk.md:199` requires append-only, tamper-evident logs, and `09:67` notes that "we can reconstruct it from logs" is not an acceptable answer to an examiner.

ClearSpend implements a per-tenant hash chain: monotonic `sequence`, `prior_hash`, and an `event_hash` over canonical JSON of the full event body including the prior hash (`audit.py:37`). `verify_chain` (`audit.py:64`) recomputes the whole chain and the result is surfaced to the Auditor role through the API and the UI. `known-limitations.md` correctly notes this detects modification but is not external notarization.

Ramp's published materials describe an audit log and an events API; they do not describe hash linking. This goes beyond the reference.

### 2.5 Other honored invariants

| Dossier requirement | Implementation |

|---|---|

| `03:25` — start as a modular monolith, Python + Postgres | Exactly that. ADR 0001. Matches both Ramp's real stack and the dossier's recommendation. |

| `02:224` — integers in the smallest currency denomination | `amount_minor BigInteger` throughout; frontend divides only at render (`api.ts:37`). |

| `09:187` — tenancy never client-supplied | ADR 0004 honored. Org and role derive from the principal; no request body accepts an organization ID. |

| `02:167` — explicit state machines, transitions not deletes | `ALLOWED_TRANSITIONS` table (`domain.py:68`), `revision` and `row_version` counters, no destructive updates on evidence. |

| `08:139` — "do better than Ramp: `Idempotency-Key` on every POST" | Present on expense submission and decisions, backed by unique constraints. Missing on policy endpoints. |

| `03:246` — fail closed on uncertainty | Consistent. Technical failure, empty checks, and any `UNKNOWN` all route to `NEEDS_REVIEW`. |

| `09:104` — never store the dangerous payload | No receipt binaries; receipts are a SHA-256 metadata reference (`db.py:133`). Minimizes scope in the same spirit as the no-PAN rule. |

| `03:246` — typed provider outcomes, visible failure | `AIProviderResult` with a closed outcome taxonomy (`ai.py:26`) and `technical_status: FALLBACK` persisted on the attempt. |

---

## 3. Defects, ranked by severity

### 3.1 Currency-blind policy thresholds

**File:** `services/backend/app/rules.py:38` and `rules.py:25`

`amount_limit` compares `facts.amount_minor <= int(params["limit_minor"])` with no reference to `facts.currency`. `receipt_required` has the same shape. `ClaimFacts` carries `currency` (`domain.py:58`) and it is never read by any rule.

`schemas.py:34` accepts any ISO-shaped code (`^[A-Z]{3}$`). The seeded policy encodes an INR 50,000 limit as `limit_minor: 5000000` (`seed.py:46`). Therefore:

- A `USD 50,000` claim submits as `5000000` minor units and **passes** an INR 50,000 limit — roughly an 83× under-enforcement at current rates

- A `JPY` claim has D=0, so its minor-unit integer is 100× smaller than the rule assumes

`02-domain-model.md:224` treats minor-unit-plus-currency as a non-negotiable invariant, and `02:204` makes the same point for the ledger: an amount without its currency is meaningless.

**Fix:** add `currency` to the rule params, and fail closed to `UNKNOWN` with a distinct reason code when the claim currency does not match — do not silently compare. The MVP is INR-only in practice, which makes this cheap to fix now and a silent money bug the first time a claim arrives in another currency.

### 3.2 Idempotency-Key replay reads another user's claim

**File:** `services/backend/app/main.py:262`

The replay lookup is scoped to `(organization_id, idempotency_key)` with no `submitter_id` predicate, and on a hit it returns `serialize_expense(existing)` — the full merchant, amount, purpose, state, recommendation, and check list.

Everywhere else, employees are correctly restricted to their own claims (`main.py:321` and `main.py:331`). This path bypasses that restriction. Any employee who reuses or guesses a colleague's key reads their claim.

`services.py:134` has the same shape for `ApprovalDecision`: a replayed key returns another reviewer's decision, including its free-text `reason`.

Practical likelihood is low with client-generated UUIDs (`page.tsx:41`), but a server must not depend on client key hygiene for authorization, and the fix is one predicate.

**Fix:** include the acting user in the replay predicate. Additionally, store a hash of the request body with the key and return `409` when the same key arrives with a different body — `08:139` recommends storing the key with the response and replaying it, which also closes this.

### 3.3 `date.today()` is used as the submission date

**File:** `services/backend/app/services.py:90`

`submitted_date=date.today()` is evaluated inside the worker, at assessment time. Two consequences:

1. **Assessments are not reproducible.** Re-running the same claim against the same pinned policy on a later date can produce a different verdict. That directly undermines the product's core promise — a decision trail that can be re-derived and defended.

2. **The submission window is re-evaluated on every resubmission.** A claim submitted on day 29, sent back with `REQUEST_INFORMATION`, and resubmitted on day 32 fails `submission_window` (`rules.py:69`) even though it was in-window when the employee first submitted. The employee is penalized for the reviewer's round trip.

**Fix:** persist `submitted_at` on the `Expense` at first submission, keep it stable across revisions, and pass it into `ClaimFacts`. Any time-dependent input to an evidence-producing computation must be captured, not read from the clock.

### 3.4 Audit sequence allocation races, taking the domain write down with it

**File:** `services/backend/app/audit.py:28`

The sequence is allocated by `SELECT ... ORDER BY sequence DESC LIMIT 1 FOR UPDATE`, then incremented in Python. Two failure paths:

- **First event for an organization:** `last` is `None`, so **no row is locked at all**. Two concurrent writers both compute `sequence = 1`.

- **Subsequent events:** T2 blocks on T1's row lock. When the lock releases, Postgres re-evaluates the predicate against *that specific row*, not the whole query — so T2 does not see T1's newly inserted higher-sequence row and re-derives the same sequence.

Either path violates `UniqueConstraint("organization_id", "sequence")` (`db.py:170`). Integrity is preserved, which is the right failure direction, but the violation is unhandled: it raises out of `append_audit`, past the handler, and rolls back the entire enclosing transaction. **The user's expense submission or decision fails with a 500.**

`docs/security/threat-model.md` lists "Duplicate or stale decisions → Idempotency keys, row locks, optimistic row version, state machine" as a current control. The row lock does not cover this case.

**Fix, in order of preference:**

1. Lock the `organizations` row (`SELECT ... FROM organizations WHERE id = :id FOR UPDATE`) before allocating. This serializes correctly in both cases, including the first event.

2. Or allocate via a dedicated per-org Postgres sequence.

3. Or wrap in a bounded retry on unique-constraint violation.

This is also the one defect an integration test would have caught, and `verification.md` already names "concurrent decisions" as a deferred test.

### 3.5 No cumulative or interval spend enforcement

Every claim is evaluated in isolation against per-claim thresholds. There is no accrued-spend concept anywhere in the schema. Forty claims of ₹49,999 each pass a ₹50,000 policy.

This is the visible symptom of the structural gap in section 4.1. It is listed here because it is a policy-enforcement hole a customer will find, not only an architectural preference.

### 3.6 Unbounded audit endpoint with O(n) verification per request

**File:** `services/backend/app/main.py:428`

`GET /api/v1/audit-events` loads every audit event for the organization, runs `verify_chain` over all of them, and serializes all of them. The frontend calls it on every render for Admin and Auditor roles (`page.tsx:21`). Cost grows linearly and without bound; the UI will time out in a pilot, not in production.

`GET /api/v1/expenses` (`main.py:314`) is likewise unpaginated.

`08-api-and-integration-surface.md:131` is emphatic:

> Ship `updated_at` cursor pagination on every list endpoint on day one. It is nearly free to design in and effectively impossible to retrofit.

`10-build-plan.md` ranks the absence of an `updated_at` cursor as failure mode #7 and notes Ramp is permanently living with it.

**Fix:** cursor pagination keyed on `(updated_at, id)` for expenses and on `sequence` for audit events. Verify the chain incrementally — anchor on the last verified hash rather than re-hashing history on every read.

### 3.7 Multi-organization principal resolution is ambiguous

**File:** `services/backend/app/security.py:27`

`User.email` is globally unique (`db.py:60`), `Membership` permits one row per `(organization, user)` and therefore N organizations per user (`db.py:66`), and the lookup uses `session.scalar` — returning an arbitrary row with no ordering.

A user who is a member of two organizations silently authenticates into whichever row the planner returns. For a system whose central security claim is server-derived tenancy, this is a soft spot.

Secondary issue on the same line: the lookup lowercases the supplied email (`demo_user.lower()`) but nothing normalizes email on write (`seed.py:23`, and there is no user-creation endpoint). A user stored with mixed-case email can never authenticate.

**Fix:** either constrain `User` to a single organization for the MVP and document it, or make the identity a `(organization, email)` pair. Normalize email to lowercase on write with a `citext` column or an explicit validator — `02:288` uses `citext` for exactly this.

### 3.8 The state-machine guard is tautological on the worker path

**File:** `services/backend/app/services.py:73` and `services.py:107`

```python

ensure_transition(ExpenseState.SUBMITTED, ExpenseState.ASSESSING)

expense.state = ExpenseState.ASSESSING

```

Both calls pass hardcoded literals rather than the row's actual state, so they assert a property of the `ALLOWED_TRANSITIONS` table, not of the expense. The guard cannot fail and cannot protect anything.

`main.py:397` (`resubmit`) sets `state = SUBMITTED` with no `ensure_transition` call at all, relying instead on the explicit `state != INFORMATION_REQUESTED` check above it — which is correct but inconsistent with the rest of the code.

The guard *is* real and load-bearing in `decide` (`services.py:156`), where it is called as `ensure_transition(ExpenseState(expense.state), target)`.

**Fix:** pass `ExpenseState(expense.state)` in both worker call sites, and route `resubmit` through the same guard. Cheap, and it makes the state machine an actual invariant rather than a documented intention.

### 3.9 Lower-severity items

| Item | Location | Note |

|---|---|---|

| Validation errors echo submitted values | `main.py:85` | `str(exc.errors())` replays the submitted `purpose` text and field values into the response body. `09:105` warns specifically that observability and error paths are where sensitive payloads leak. Return codes and field paths only. |

| `ExpenseState.DRAFT` is unreachable | `domain.py:17`, `db.py:128` | Declared in the state machine; the column defaults to `SUBMITTED` and nothing ever writes `DRAFT`. |

| `AIProviderResult.retryable` is never read | `ai.py:30` | Set on three code paths, consumed nowhere. Implies retry behavior that does not exist — `graph.py:51` treats every non-success as terminal technical failure. |

| OpenAI timeout branch is unreachable | `ai.py:87` | The OpenAI SDK raises `APITimeoutError`, not the builtin `TimeoutError`. Timeouts are therefore classified as `provider_error`. Both are `retryable=True` so behavior is unchanged, but the outcome taxonomy is inaccurate — which matters because the taxonomy is presented as a control in `threat-model.md`. |

| Attempt selection is order-ambiguous | `services.py:40`, `services.py:144` | `max(expense.attempts, key=created_at)` with no relationship ordering and no tiebreak. Ties are possible within a transaction. Prefer ordering by `(revision, created_at, id)`. |

| `Idempotency-Key` missing on policy endpoints | `main.py:118`, `main.py:172` | Draft creation and publication are both non-idempotent POSTs. `08:139` says every POST. |

| No rate limiting anywhere | — | `08:99` documents Ramp's 200-per-10s rolling window. No limit, no `429`, no admission gate. |

---

## 4. What needs adding

### 4.1 A fund or budget primitive — the largest structural divergence

This is the most consequential finding in the review.

`10-build-plan.md` ranks "limits on the card instead of a fund object" as failure mode #6. `02-domain-model.md:121` makes the design point:

> The budget is not on the card and not on the user. It is a separate object that cards, users, and reimbursements all reference.

And `05-payments-and-ap-rails.md:140` addresses the reimbursement case directly — which is precisely ClearSpend's scope:

> Reimbursements are gated by **funds**, the same primitive that backs cards... This is the strongest argument for the fund-centric model. One policy object governs both pre-spend (card authorization) and post-spend (reimbursement eligibility). If you model card limits and reimbursement policy separately, they will drift.

ClearSpend has organization-wide `PolicyRule` rows attached to `PolicySection`. There is no budget object, no `interval` (`DAILY` / `MONTHLY` / `ANNUAL` / `TOTAL`), no membership, and no accrued-spend tracking. Concrete consequences today:

- **Team and per-person budgets are inexpressible.** "Marketing gets ₹50k per quarter across six people in four categories" has no representation. Policy is one flat set of rules for the whole tenant.

- **No velocity or cumulative enforcement** (defect 3.5). Each claim is scored alone.

- **No shared-budget attribution**, which `01-product-surface.md:16` lists as a core capability of the category.

- **Every later phase gets harder.** `10-build-plan.md:181` notes that Agent Cards are cheap if the fund primitive was built right in Phase 1 and expensive if it was not. The same logic applies to any per-team policy, any pre-approval flow, and any card extension.

The minimum viable version is small and fits the existing shape:

```

fund(id, organization_id, display_name, status,

limit_minor, limit_currency, interval,

allowed_categories)

fund_member(fund_id, user_id)

```

plus an `interval_spend(fund_id, interval)` aggregate over approved claims, and two new rule types — `fund_interval_limit` and `fund_category` — registered in `validate_rule_params` (`domain.py:101`). Claims reference a fund; the fund denormalizes its restrictions at creation exactly as `02:356` recommends, so evaluation never joins through a table an admin may be editing.

Done now this is perhaps two days of work. Deferred, it is a schema migration across every claim, decision, and audit record.

### 4.2 Cursor pagination on every list endpoint

Covered in defect 3.6. Restated here because the dossier frames it as an addition rather than a bug: `08:131` calls it nearly free to design in and effectively impossible to retrofit, and `10-build-plan.md:55` calls it "the cheapest insurance in the entire plan."

### 4.3 Designed payout states, declared now even if unreachable

`05-payments-and-ap-rails.md:128`:

> `FAILED_REIMBURSEMENT` as a first-class state matters — payouts to employee bank accounts fail (closed account, wrong routing number) and the expense must return to an actionable state rather than disappearing.

ClearSpend terminates at `APPROVED` (`domain.py:76`), which is defensible while money movement is out of scope. The cost is that the terminal set is a claim about the domain, and changing it later touches the state machine, the audit vocabulary, and every UI branch.

Declaring `AWAITING_PAYMENT`, `PAID`, and `FAILED_REIMBURSEMENT` now — reachable only when a payout adapter exists — costs a handful of lines and preserves the seam. Ramp's published enum (`02:210`) is the reference shape.

### 4.4 Close the correction feedback loop — the data is already there

`07-ai-ml-and-agents.md:65` notes that every user correction is a labeled training example, and `10-build-plan.md:202` makes the sharper point: there is no labeled data for automation until humans have made the decisions.

ClearSpend already captures the dataset. `ApprovalDecision` stores `observed_recommendation`, the human `action`, and the mandatory `reason`, and `services.py:151` computes the `override` boolean and writes it into the audit metadata. This is exactly the reviewer-agreement corpus the dossier describes.

Nothing reads it. There is no override-rate query, no reviewer-agreement metric, no surface anywhere. `PRODUCT_ARCHITECTURE_AND_EXECUTION_PLAN.md` names reviewer override rate as one of four explicit guardrail metrics, and the primary success metric is median reviewer time per claim — which is derivable from the audit chain timestamps and is also not computed.

**Add:** a small metrics endpoint or report over `ApprovalDecision` and `AuditEvent` producing override rate by reason code, agreement rate by recommendation class, and median time from `expense.assessed` to decision. This is the product's core evidence claim and it is currently one SQL query away from existing.

### 4.5 A real evaluation harness with separated scoring

`03-architecture.md:248`:

> Build shadow evaluation into the policy engine from the start; you will need it every time you change decisioning logic.

`07-ai-ml-and-agents.md:144` adds the design insight — evaluate the agent and the policy as **separate, isolated systems**, because a combined end-to-end metric cannot distinguish "the agent looked at the wrong data" from "the model made a bad call," and those have opposite fixes.

Current state: `evals/manifest.yaml` names four required case IDs (`clear-pass-001`, `prohibited-alcohol-001`, `missing-receipt-001`, `injection-receipt-001`) and references `config/release-policy.yaml`. Neither file has a runner, a dataset, or a consumer. See section 6 for the claim mismatch.

**Add:** the four named cases as real fixtures, a runner that scores deterministic rule correctness separately from AI citation validity and status calibration, and a CI job whose name matches the release policy.

### 4.6 Audit logging at the write-dispatch boundary

`09-compliance-and-risk.md:193`, on Ramp's agent documentation stating that every write lands in the audit log automatically with no extra wiring:

> That phrasing matters: audit logging is at the write dispatch boundary, not in each handler. Handler-level audit logging is audit logging with holes in it.

ClearSpend has five hand-placed `append_audit` calls. Today the coverage appears complete. The structure guarantees that the sixth mutating endpoint someone adds will be the one that forgets.

**Add:** either a SQLAlchemy event hook on the mutating session flush, or a single write-dispatch helper that every state change routes through. This also fixes the ordering problem in 3.4 in one place rather than five.

### 4.7 Prompt version recorded on the attempt

`PRODUCT_ARCHITECTURE_AND_EXECUTION_PLAN.md` states as a trust requirement: "Policy, prompt, engine, and model versions are recorded."

`AssessmentAttempt` records `engine_version`, `provider`, and `model` (`db.py:147`). It does not record the prompt. The instruction string is an inline literal at `ai.py:70`, so changing it silently changes the meaning of every subsequent assessment with no trace in the evidence record.

**Add:** a `prompt_version` or content hash of the instruction string, persisted on the attempt. Two lines, and it is required by the project's own stated criteria.

### 4.8 The missing middle rung of the coding ladder

`07-ai-ml-and-agents.md:87` prescribes three layers: deterministic per-customer memory (handles the head of the distribution, free and explainable), a global model (the body), then an LLM for genuinely novel cases only (the tail). It warns explicitly against inverting this.

ClearSpend has layer 1 and layer 3 with nothing between. At MVP scale this is the right simplification, and the ordering is correct — deterministic first, LLM last. Worth noting only so that the middle rung is a conscious future addition rather than a discovery.

---

## 5. What needs removing

### 5.1 Vendored third-party agent skills — 1.5 MB of a 1.8 MB repository

`.agents/` (900 KB) and `.claude/` (680 KB) contain roughly 40 vendored skills plus `skills-lock.json`. Several have no relationship to this codebase at all:

- `migrate-to-shoehorn` — migrating TypeScript test files to `@total-typescript/shoehorn`

- `scaffold-exercises` — creating course exercise directories

- `setup-ts-deep-modules` — TypeScript dependency-cruiser configuration

- `setup-matt-pocock-skills`, `ask-matt`, `writing-beats`, `writing-fragments`, `writing-shape`

This is TypeScript-course tooling inside a Python and Next.js finance application. Two reasons to cut it:

1. The submission asks for the codebase. 83% of the repository being unrelated vendored agent configuration reads as unexamined scaffold.

2. The integrity bar in the problem statement requires crediting third-party assets and respecting licenses. Bulk-vendored skills with a lock file and no attribution note sit awkwardly against that.

**Keep** the skills actually used in this project's workflow — `code-review`, `tdd`, `domain-modeling`, `diagnosing-bugs` are plausible. Remove the rest, and add a one-line provenance note for what remains.

### 5.2 Dead or misleading declarations

| Remove or wire up | Location |

|---|---|

| `opentelemetry-api` dependency | `pyproject.toml:11` — declared, never imported anywhere in `app/` |

| `AIProviderResult.retryable` | `ai.py:30` — never consumed |

| `ExpenseState.DRAFT` | `domain.py:17` — unreachable |

| `AssessmentAttempt.latency_ms` | `db.py:152` — always 0, never written |

| `Settings.log_level` | `config.py:17` — never read; `structlog` is never configured |

| `except TimeoutError` branch | `ai.py:87` — unreachable with the OpenAI SDK |

Each is small. Collectively they are the difference between a codebase that describes itself accurately and one that does not, which is the subject of the next section.

---

## 6. Documentation that overstates the implementation

The problem statement's integrity bar is explicit — do not fabricate metrics or outcomes, and verify generated work. These are not code defects but they are the highest-risk items in the submission, because each one is a checkable claim that does not hold.

| Claim | Where | Reality |

|---|---|---|

| Telemetry status `implemented_mvp`; "OTel traces/metrics/log redaction" marked P0 | `docs/evidence/rubric-matrix.csv`; `TECHNICAL_ARCHITECTURE_IMPLEMENTATION_PLAN.md:1215` | `opentelemetry-api` is a declared dependency and is never imported. No spans, no metrics, no exporter. What exists is a correlation ID and two `structlog` call sites. |

| "JSON logs + error tracking + metrics" | `PRODUCT_ARCHITECTURE_AND_EXECUTION_PLAN.md:299` | `structlog` is never `.configure()`d, so it falls back to the default console renderer — not JSON. No error tracking. No metrics. |

| Assessment latency is measured | `db.py:152` | `latency_ms` defaults to 0 and is never assigned. |

| "CI repeats these checks from lockfiles" | `docs/engineering/verification.md` | `make lint` runs `mypy --strict`; `.github/workflows/ci.yml` runs `ruff` and `pytest` only. **mypy is not in CI**, so the strictest gate is local-only. |

| Release policy requires `backend-unit`, `backend-property`, `frontend-typecheck`, `compose-validation` | `config/release-policy.yaml` | CI job names are `backend`, `frontend`, `containers`. Nothing reads the release policy. The gate is decorative. There is also no `tests/property` directory — Hypothesis tests live inside `tests/unit/test_domain.py`. |

| Eval suite requires four named case IDs | `evals/manifest.yaml` | No runner, no dataset, no cases. The directory contains only the manifest. |

| "Policy, prompt, engine, and model versions are recorded" | `PRODUCT_ARCHITECTURE_AND_EXECUTION_PLAN.md` §2 | Prompt version is not recorded. See 4.7. |

| "Duplicate or stale decisions → row locks" | `docs/security/threat-model.md` | The row lock does not cover audit sequence allocation. See 3.4. |

| ADR 0003: "queue latency, connection utilization, and outbox age are operational signals" | `docs/adr/0003` | None of the three is measured, queryable, or alerted on. |

**Also:** `alembic/versions/0001_initial.py` calls `Base.metadata.create_all()` and its `downgrade` calls `drop_all()`. That is not a migration — it is schema generation wearing a migration's filename, with no incremental path and a destructive rollback. `seed.py:61` calls `create_all()` a second time, so the schema has two independent authorities that can drift. `verification.md` promises a future "migration rollback" test that this design cannot meaningfully support.

### Testing gap behind the claims

Three unit test files, 159 lines total, all pure-function. There is no Postgres in CI and therefore no test of:

- Tenant isolation (asserted only in `scripts/smoke.py`, which requires a running stack)

- Idempotency replay on either endpoint

- Concurrent decisions and the `row_version` conflict path

- Audit chain append under concurrency — the defect in 3.4

- Outbox relay and recovery

- `decide()` override detection and the reason requirement

- Any HTTP endpoint at all

`verification.md` names most of these as deferred, which is honest. But `rubric-matrix.csv` marks Risk tests as `implemented_mvp`, and the assignment's engineering rubric asks that "meaningful tests cover risk." The riskiest code in the repository — `services.py` and `main.py`, roughly 640 lines including all the money and authorization logic — has zero direct coverage. Adding a `pytest` fixture that spins Postgres via `docker compose` or `testcontainers` and covering the six paths above is the highest-value engineering work available, and it would have caught defects 3.2 and 3.4.

---

## 7. One item to verify

`config.py:16` — `openai_model: str = "gpt-5.6-terra"`, also in `.env.example:6`. This is not a model identifier I can confirm exists. Verify against the current OpenAI model list before it ships as a default, since a wrong default silently routes every live assessment into a provider error and therefore into `NEEDS_REVIEW` — a failure that is safe but invisible.

---

## 8. Summary

**The judgment is right.** ClearSpend honors the dossier's single most important rule — `07:138`, that deterministic policy and calibrated models decide while the language model only orchestrates and explains — more cleanly than most systems that claim to. Deterministic-first evaluation, AI as advisory-only, fail-closed aggregation, allowlisted citations, mandatory override reasons, and a hash-linked audit trail together form a coherent and genuinely defensible trust story. ADRs 0001–0004 read as if written directly from dossier files `03`, `07`, and `09`, and the outbox and policy-versioning implementations are faithful rather than cargo-culted. The policy versioning is better than the reference product's published model, and the audit chain exceeds it.

**The mechanics trail the judgment.** In priority order:

1. Fix the currency-blind thresholds (3.1) — a money bug.

2. Fix the idempotency authorization hole (3.2) — one predicate.

3. Persist `submitted_at` (3.3) — reproducibility is the product's core claim.

4. Fix audit sequence allocation (3.4) — currently a 500 that discards the user's write.

5. Add the fund primitive (4.1) — the structural gap; cheap now, a migration later.

6. Add cursor pagination (4.2) — free now, permanent tax later.

7. Reconcile the documentation with the code (§6) — before anyone grades the integrity criterion.

8. Add Postgres-backed integration tests for the six uncovered risk paths (§6) — would have caught items 2 and 4.

Items 1–4 and 8 are days of work. Item 5 is the one that compounds. Item 7 is the one that is cheapest to fix and most expensive to be caught on.