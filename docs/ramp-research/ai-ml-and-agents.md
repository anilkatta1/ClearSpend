# 07 — AI, ML, and Agents

Ramp's CTO has said the "smart automation layer" on top of the card is what Ramp built in-house while treating the card rails as a commodity to buy. This file is that layer.

## ML platform

Sourced from Ramp's engineering blog:

| Component | Technology |

|---|---|

| ML framework | **Metaflow** — training, model management, versioning, deployment |

| Orchestration | **Airflow** — "battle-tested, Python-based, the de facto tool in data engineering" |

| Warehouse | **Snowflake** |

| Data transport | **Apache Arrow** — cut Snowflake fetch memory growth by up to 79% |

| Infrastructure | AWS managed services wherever possible |

The stated design goal: leverage AWS-managed services on the infrastructure side, while letting data scientists and MLEs "get up and running quickly" and "access all layers of the full stack of machine learning, from data and compute to versioning and deployment" while staying in Python.

`[recommendation]` The Arrow detail is a real cost lever, not trivia. Pulling training data out of a warehouse through a row-oriented driver into pandas is where ML infrastructure budgets go to die. Use Arrow-native transport from the start.

## Receipt OCR and matching

The flagship automation, and the most thoroughly documented.

### Pipeline

```

receipt image (mobile / SMS / email / Slack / Teams)

▼

OCR extraction — merchant, date, amount, line items

▼

candidate transaction retrieval (card + date window + amount range)

▼

match scoring

▼

auto-verify OR suggest OR no match → prompt user

▼

GL category assignment

```

### The auto-verify rule

Published: a receipt passes if **2 of 3 fields — amount, date, merchant — match**.

That threshold is the whole design in one line. Requiring 3 of 3 fails constantly on real receipts. Requiring 1 of 3 matches the wrong transaction. Two of three is the empirical sweet spot, and it is the kind of number you can only arrive at by measuring, not by reasoning.

### What actually goes wrong

Ramp published a post on using Apple Intelligence for on-device receipt matching — running `Vision.RecognizeTextRequest` locally to extract text, checking whether it contains the merchant name, transaction amount, and/or transaction date, and storing the match outcome in a local database.

Their stated findings on real-world data being "messier than expected":

- **Amounts formatted differently** — `1,234.56` / `1234,56` / `$1234.56` / `1.234,56`

- **Merchant names abbreviated** — "Amazon Web Services" appears as "AWS"

- **Merchants with multiple names** — Facebook / Meta

Every one of those is an entity-resolution problem, not an OCR problem. The OCR reads the pixels correctly and the match still fails.

`[recommendation]` Budget more engineering for normalization and alias resolution than for OCR itself. OCR is a bought commodity — Ramp partners with **Taggun** for receipt and invoice OCR, and separately uses on-device Apple Vision. Matching is where the product lives. Concretely, you need:

- Merchant alias table, seeded from card-network normalized descriptors and grown from user corrections

- Currency-aware amount parsing with locale-specific separator handling

- Fuzzy string matching (token set ratio, not raw Levenshtein — "AWS" versus "Amazon Web Services" fails Levenshtein badly)

- Embedding similarity for the hard cases (see transaction embeddings below)

- A correction feedback loop, because every user fix is a labeled training example

### On-device inference

The Apple Intelligence work is strategically interesting beyond the technical detail: OCR on-device means the receipt image never leaves the phone for extraction. That is a privacy and cost win simultaneously — no per-page OCR fee, no image egress, no PII in your OCR vendor's logs.

`[recommendation]` Do the extraction on-device where the platform supports it, and send structured fields plus the image to the server. Keep a server-side fallback for web uploads and older devices.

### Digital receipts

Ramp auto-generates receipts for transactions under **$75**, sourced from POS data — $75 being the IRS substantiation threshold below which a receipt is not required for most business expenses.

This is the highest-leverage feature in the whole expense module and it involves no ML. Most transactions are small. If most transactions need no receipt, most of the work disappears. `[recommendation]` Find the equivalent rule in your target jurisdiction and implement it before you optimize your matcher.

Ramp also ingests receipts directly from merchant integrations — Amazon Business, Uber, Lyft — plus Gmail and Outlook. `[recommendation]` Direct merchant feeds beat OCR on every dimension: structured, complete, line-itemized, free. Prioritize the top 20 merchants by transaction count over improving your OCR model.

## Categorization and coding

- Auto-categorization and GL code assignment, described as trained on 70,000+ customer transaction patterns.

- An accounting rules engine auto-codes recurring vendors — once Figma always maps to Software and AWS to Infrastructure, coding is deterministic.

- Learns from corrections over time.

`[recommendation]` The layering matters and is easy to get backwards:

```

1. Deterministic rules — per-customer vendor→GL memory. Fires on most volume. Free, instant, explainable.

2. Global model — cross-customer patterns for the long tail. Cheap.

3. LLM — genuinely novel merchants only. Expensive, rate-limited, slow.

```

Do not put an LLM at layer 1. A customer who has coded Figma to Software forty times does not need inference; they need a lookup. The rules engine handles the head of the distribution, the model handles the body, the LLM handles the tail. Inverting this is how you get a large model bill and worse accuracy than a dictionary.

## Published ML work worth studying

From Ramp's engineering blog. Each one is a solved problem you would otherwise re-solve.

**Transaction embeddings for retrieval.** Embedding transactions to improve search and similarity. `[inferred]` This is the substrate for merchant resolution, duplicate detection, anomaly detection, and "find transactions like this one" search — one embedding space, many features.

**RAG for industry classification.** Retrieval-augmented merchant/industry classification, replacing an earlier approach. Directly relevant to MCC-to-category mapping and to vendor enrichment.

**Merchant matching with AI.** A dedicated post on fixing merchant matches — confirming that merchant identity resolution is a standing ML problem at scale, not a one-time data-cleanup task.

**Thompson sampling for LLM routing.** Online learning for cost-efficient model routing — treating "which model should serve this request" as a multi-armed bandit, exploring cheaper models and exploiting the ones that perform. `[recommendation]` This is the single most reusable idea on Ramp's blog for anyone running LLM features at volume. Static routing rules go stale the week a new model ships; a bandit adapts automatically and gives you cost reduction with a measured quality floor.

**AI spend management as a product.** Ramp both built internal token-spend tracking and shipped it as a customer-facing product, with `/ai-spend/api-keys`, `/ai-spend/team`, `/ai-spend/usage` endpoints and an inbound `POST /developer/v1/ai-usage/unified` for platforms to broadcast usage. Note the schema exception: AI usage reports `reported_cost.amount` as a **decimal string**, not a minor-unit integer — because token costs go below one cent.

**Agentic engineering internally.** Posts on an AI on-call assistant, self-writing integrations, fixing ~100 security issues in six days with zero humans, and a custom background agent. Not product features, but a signal about where their engineering leverage comes from.

## Risk and fraud ML

Ramp's "Agentic Risk Operations" post is the clearest published statement of how to build AI into a financial system responsibly, and its central principle should govern your entire design.

Context: **$200B+ annual payment volume, 35+ countries.**

### Architecture

```

1. Universal intake — Zendesk, Slack, internal tooling

2. Triage — pull business context (financials, payment history),

classify request type and complexity

3. Policies and models — as callable TOOLS

as tools

4. Decision routing — to the right internal team, or direct to customer

```

### The governing principle

Stated directly: **"risk-based decisions are often predictions in disguise."** Deciding when to release a payment depends on modeling "the probability of a debit returning," which Ramp treats as a machine learning problem rather than something an agent reasons through.

So: **agentic reasoning handles orchestration; it does not make the risk judgment.** Decisions are delegated to "machine learning models trained on millions of historical data points," with agents acting as routers that call those models. Every autonomous decision remains auditable and governed under an approved policy.

`[recommendation]` This is the most important architectural rule in this entire dossier for anyone building AI into a money system. Write it on the wall:

> **The agent decides *what to look up* and *where to send the answer*. A calibrated model or a deterministic policy decides *the answer itself*.**

An LLM cannot give you a calibrated probability, cannot be backtested against outcomes, cannot be explained to a regulator, and cannot be held to a threshold. A gradient-boosted model on structured features can do all four. Use the LLM for the parts that are genuinely language problems — reading a document, drafting a customer reply, classifying an intent — and never for the part where being 3% miscalibrated costs real money.

### Evaluation

Agents and policies are evaluated as **separate, isolated systems**:

- **Agent evaluation** — scored on context-gathering accuracy and correct routing behavior

- **Policy evaluation** — scored against actual downstream risk outcomes

The dataset: **a benchmark of more than 1,000 payment operations**, built from operator feedback, each labeled with tool-call trajectory, operator agreement, and real risk outcome. Used both for live monitoring and for catching pre-deployment regressions.

`[recommendation]` The separation is the insight. A combined end-to-end metric cannot tell you whether a bad outcome came from the agent looking at the wrong data or the model making a bad call — and those have opposite fixes. Instrument the trajectory, not just the outcome.

### Rollout ladder

1. Agents run **alongside** human operators, who give live feedback on each decision.

2. Track outcome distribution, human-agent alignment, latency, and token usage to assess readiness.

3. On meeting thresholds, agents get a capped **"exposure budget"** — a limit on total dollar risk carried at once.

4. Scale by incrementally raising the budget, across both operation types and dollar volume.

Plus: **shadow mode** against live traffic before deployment, and operators can adjust "agent skills and tool configurations" without engineering involvement.

`[recommendation]` The **dollar-denominated exposure budget** is a primitive you should build early and apply to everything automated, not just agents. Rate limits cap how *often* an automated system acts. Exposure budgets cap how much *damage* it can do. They are not substitutes. A system making 10 automated decisions a minute on $50 transactions and one on a $2M wire needs the second control, not the first.

### Reliability

- Async execution framework resilient to network and infrastructure failure

- **Automatic failover to backup model providers** when a primary is down

- Centralized observability per agent interaction

Multi-provider LLM failover is not optional for a production financial system. Model APIs have outages.

## Agentic payments

Ramp's newest surface, and the most forward-looking part of the platform.

### Agent Cards

A purchase-scoped credential for agent-driven checkout: **merchant- and amount-scoped, requested immediately before one checkout.** Explicitly *not* for subscriptions or later merchant charges — reusable spend goes on a Virtual Card. Requires at least one active fund.

`[inferred]` This is the correct primitive for agent commerce and it falls straight out of the existing model. An agent gets a credential that can be used exactly once, at exactly one merchant, for at most one amount. The authorization engine already enforces merchant and amount restrictions, so an Agent Card is a fund with a maximally narrow restriction set and a single-use card. No new infrastructure — just a new configuration of the existing spend-control primitive. That is what a good abstraction buys you.

### MCP surface

- Production: `https://mcp.ramp.com/mcp`

- Demo/sandbox: `https://demo-mcp.ramp.com/mcp`

- One MCP connection per business for multi-business setups

- Capabilities are grouped "by what the agent does for the user, not by tool name," with an explicit warning that "specific tool names will drift" as tools ship continuously

- A CLI built on `https://api.ramp.com/agent-tools` endpoints, which are **not** accessible to external clients

- The CLI's `agentic-purchase` skill composes multiple MCP tool calls into one workflow: **request credential → checkout → audit**

### Agent auth

| Property | Value |

|---|---|

| First use | Browser OAuth |

| Read-only session expiry | 1 week after last use |

| Read-write session expiry | **24 hours after last use** |

| Renewal | Any call within the window keeps the session alive indefinitely |

| Remote hosts | Authenticate locally, copy the session config |

| Config location | `~/.config/ramp/config.toml` — "treat like a credential, never commit" |

| External MCP clients | Must authorize through the shared Ramp MCP OAuth client, **not** their own Developer API OAuth app |

Plus two enforcement guarantees:

- **Every write action, on any channel, lands in the customer's audit log automatically** — no extra wiring.

- **Permissions are enforced per-user:** employees see only their own data, admins see company-wide data.

`[recommendation]` Three things to copy here.

**Differential session lifetimes by capability.** A read-only agent session lasting a week is fine. A read-write session lasting a week is a standing authorization to move money from a config file on a laptop. 24 hours with sliding renewal is the right shape: convenient for active use, self-healing for abandoned credentials.

**Agent identity inherits user permissions, never exceeds them.** An agent acting for an employee sees exactly what that employee sees. This is the only defensible model — a privileged service account that agents share is a confused-deputy vulnerability with a money-movement payload.

**Audit logging at the write boundary, not in each handler.** If audit logging is something each endpoint remembers to do, some endpoint will forget. Put it at the boundary where writes are dispatched and it cannot be forgotten.

### Protocols

Ramp's public documentation names **only MCP**. No mention of AP2, x402, ACP, or other agent-payment protocols. `[inferred]` They are building on the assistant-integration protocol that exists and has adoption, rather than betting on a payment-specific agent protocol that does not yet have it. For a clone, that is the right call — MCP gets you into Claude, ChatGPT, and Copilot today. Watch the payment-protocol space but do not build against it speculatively.

Ramp also published a post titled "We Tested Marketing Incentives to AI Agents. Here's What Happened." `[inferred]` They are already treating agents as a distribution channel and studying how agents choose vendors. If agent-mediated purchasing becomes material, being the credential layer agents reach for is a strategically enormous position — which is presumably why a company with seven products shipped Agent Cards.

