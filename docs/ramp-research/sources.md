# Sources

Research conducted 2026-09-11 via live web search and fetch. Grouped by type.

## Ramp developer documentation (primary, highest reliability)

Ramp publishes LLM-readable plain-text versions of its docs. These were the primary source for the domain model, API surface, and state machines.

- [Ramp API Documentation](https://docs.ramp.com/) — root

- [`/llms.txt`](https://docs.ramp.com/llms.txt) — full documentation index

- [`/llms-api.txt`](https://docs.ramp.com/llms-api.txt) — generated endpoint and schema reference (large; truncates on fetch)

- [`/openapi/developer-api.json`](https://docs.ramp.com/openapi/developer-api.json) — canonical OpenAPI spec, not fully retrieved

- [Data relationships](https://docs.ramp.com/llms-guides/data-relationships.txt) — the three-vendor model, entity relationships

- [Cards and funds](https://docs.ramp.com/llms-guides/cards-and-funds.txt) — card types, fund concept, vault scopes

- [Spend controls](https://docs.ramp.com/llms-guides/spend-controls.txt) — funds, spend programs, approvals

- [Spend programs](https://docs.ramp.com/llms-guides/spend-programs.txt) — template model, `is_shareable`, `permitted_spend_types`

- [Virtual cards](https://docs.ramp.com/llms-guides/virtual-cards.txt) — iframe vs vault, PCI scope, termination

- [Bill Pay](https://docs.ramp.com/llms-guides/bill-pay.txt) — bill object, nested payments, rails, vendor model

- [Reimbursements](https://docs.ramp.com/llms-guides/reimbursements.txt) — lifecycle, direction, multi-currency fields

- [Procurement](https://docs.ramp.com/llms-guides/procurement.txt) — intake to PO

- [Procurement intake](https://docs.ramp.com/llms-guides/procurement-intake.txt) — integration workflow

- [ERP integrations](https://docs.ramp.com/llms-guides/erp-integrations.txt) — sync architecture, coding model, filter rules, error taxonomy

- [Banking](https://docs.ramp.com/llms-guides/banking.txt) — account type enums, balance history, treasury scope

- [Applications](https://docs.ramp.com/llms-guides/applications.txt) — KYB/KYC fields, beneficial ownership, status machine

- [Authorization](https://docs.ramp.com/llms-guides/authorization.txt) — OAuth flows, token lifetimes, complete scope list

- [Webhooks](https://docs.ramp.com/llms-guides/webhooks.txt) — complete event catalog, HMAC signing, retry semantics

- [Users](https://docs.ramp.com/llms-guides/users.txt) — role and status enums, org model, deferred creation

- [Monetary values](https://docs.ramp.com/llms-guides/monetary-values.txt) — minor units, FX fields, rounding

- [Rate limits and timeouts](https://docs.ramp.com/llms-guides/rate-limiting.txt) — quotas, pagination, incremental sync warnings

- [Build for AI agents](https://docs.ramp.com/llms-guides/build-for-ai-agents.txt) — Agent Cards, MCP surface, agent session auth

- [Customized approvers](https://docs.ramp.com/llms-guides/customized-approvers.txt) — approver matrix tables on custom records

- Not fetched but indexed and relevant for deeper work: `ramp-rate`, `incorporation`, `custom-records`, `deferred-tasks`, `banking`, `ai-usage`, `mcp`, `ramp-data-mcp`, `cli`, `sandbox`, `export-to-a-data-warehouse`, `conferma-onboarding-request`, `error-handling`, `pagination`, `user-lifecycle`, `changelog`

- [Developer API overview (support)](https://support.ramp.com/accessing-the-developer-api)

- [Developer Platform](https://ramp.com/developer-tools)

## Ramp engineering blog

Note: `engineering.ramp.com` / `builders.ramp.com` render client-side, so individual posts largely could not be fetched directly. Content below came from search-result summaries and from the [engineering.fyi mirror index](https://www.engineering.fyi/company/ramp).

Fetched successfully:

- [Abstraction Engineering (workflows engine)](https://engineering.ramp.com/post/workflows) — the graph engine, Postgres persistence, INSERT CTEs, Postgres-backed Celery broker, DSL compilation, 45M+ runs

- [Agentic Risk Operations](https://engineering.ramp.com/post/agentic-risk-operations) — policies-and-models-as-tools, exposure budgets, shadow mode, 1,000-operation benchmark, $200B volume

Indexed and directly relevant, not fetched:

- [Automating Receipt Collection: Apple Intelligence for On-Device Inference](https://engineering.ramp.com/post/apple-intelligence-receipt-matching)

- [How Ramp Accelerated Machine Learning Development](https://engineering.ramp.com/post/metaflow-production-ml) — Metaflow, Airflow

- [Online Learning for Cost-Efficient LLM Routing](https://engineering.ramp.com/post/thompson-sampling-model-routing)

- [Apache Arrow Cut Snowflake Fetch Memory Growth by Up to 79%](https://engineering.ramp.com/post/apache-arrow-ml-data-loading)

- [Agentic identity: modeling agents to keep users in control](https://engineering.ramp.com/post/agent-identity-introduction)

- [Building a Unified Pipeline for AI Token Spend](https://engineering.ramp.com/post/ai-token-spend-management)

- [We Tested Marketing Incentives to AI Agents](https://engineering.ramp.com/post/marketing-to-ai-agents)

- Moving Fast by Moving Slow: How We Built Payments at Ramp

- Building Ramp's MCP server

- How Ramp Fixes Merchant Matches with AI

- Improving Retrieval on Ramp with Transaction Embeddings

- From RAG to Richness: How Ramp Revamped Industry Classification

- Increasing velocity by modernizing a Python codebase

- Rate limiting with Redis

- Finding the right balance of speed and security through just-in-time access to cloud resources

- What I learned taking Ramp Bill Pay from 0 to N

- Cost Efficient Snowflake CI

- Elixir at Ramp

- [Full index](https://builders.ramp.com/)

## Interviews and analyst research

- [Karim Atiyeh (Ramp co-founder/CTO) on the card issuing market — Sacra](https://sacra.com/research/karim-atiyeh-ramp-expert-interview-card-issuing/) — build-vs-buy framing, processor selection criteria, switching optionality, interchange politics

- [Ramp Business Breakdown & Founding Story — Contrary Research](https://research.contrary.com/company/ramp) — most complete public product surface inventory, partner dependencies, competitive landscape, acquisitions

- [Ramp revenue, valuation & funding — Sacra](https://sacra.com/c/ramp/)

- [Banking-as-a-Service Market Map for Card Issuance](https://chingjon.medium.com/banking-as-a-service-market-map-for-card-issuance-63284057407) — the Ramp/Marqeta/Sutton stack layering

- [Marqeta IPO analysis — CB Insights](https://www.cbinsights.com/research/marqeta-ipo-payments-tech/) — Sutton Bank settling 96% of Marqeta volume

## Business model and economics

- [How Does Ramp Make Money — ValueAdd VC](https://valueaddvc.com/blog/how-does-ramp-make-money-card-interchange-software-fees-and-the-business-model-breakdown) — ~250bps gross / ~200bps to bank / ~50bps net; 70/15/rest revenue mix

- [Ramp's Growth Playbook: $0 to $1B+ Revenue in 6 Years](https://www.startupriders.com/p/ramp-growth-playbook) — take-rate compression mechanics

- [Ramp Stock: $32B Valuation — TSG Invest](https://tsginvest.com/ramp/)

## Bank and processor partners

- [Ramp statement on issuing banks (Sutton, Celtic)](https://twitter.com/tryramp/status/1634288306799222785)

- [Ramp Corporate Card Review — Merchant Maverick](https://www.merchantmaverick.com/reviews/ramp-corporate-card-review/)

- [Marqeta program management](https://www.marqeta.com/payment-solutions/program-management)

- [The Rise of FinTech Partner Banks — FinTechtris](https://www.fintechtris.com/blog/the-rise-of-fintech-partner-banks)

## Ramp product pages

- [Ramp home](https://ramp.com/) — current product module navigation

- [Spend management](https://ramp.com/spend-management)

- [Corporate cards](https://ramp.com/corporate-cards)

- [Expense management](https://ramp.com/expense-management)

- [Receipt automation](https://ramp.com/receipt-automation)

- [Introducing Ramp receipt automation](https://ramp.com/blog/ramp-receipt-automation)

- [How Receipt Scanning Works in Expense Management Software](https://ramp.com/blog/receipt-scanning-expense-management) — OCR pipeline, Taggun partnership, 2-of-3 auto-verify

- [AI Expense Management guide](https://ramp.com/blog/ai-expense-management)

## Ledger design (background, not Ramp-specific)

Used for the ledger recommendations in `03-architecture.md`, which are my design guidance rather than a description of Ramp's internals.

- [Double-Entry Ledgers: The Missing Primitive in Modern Software — Paul Gross](https://www.pgrs.net/2025/06/17/double-entry-ledgers-missing-primitive-in-modern-software/)

- [Build a Bank Ledger in Go with PostgreSQL using Double-Entry Accounting — freeCodeCamp](https://www.freecodecamp.org/news/build-a-bank-ledger-in-go-with-postgresql-using-the-double-entry-accounting-principle/)

- [ERP General Ledger: Designing a Double-Entry Core in PostgreSQL](https://www.matthewswong.com/en/blog/erp-general-ledger-double-entry-design/) — the deferrable constraint trigger pattern

- [pgledger discussion — Lobsters](https://lobste.rs/s/9sxdp3/ledger_implementation_postgresql)

## Known gaps in this research

Things I could not verify and that would materially improve the blueprint:

- **Ramp's actual ledger schema.** Not published. All ledger design in this dossier is my recommendation.

- **The full OpenAPI spec.** `/openapi/developer-api.json` and `/llms-api.txt` both exceed fetch limits. The complete field-level schema for transactions, physical cards, purchase orders, item receipts, and statements was not retrieved. `/llms-api.txt` truncated at the `bills` resource. **If you want field-level precision, download `/openapi/developer-api.json` directly and generate types from it.**

- **Blank Canvas approvals.** Referenced repeatedly across guides (`blank_canvas:write` scope, `unified_requests.external_approval_request` webhook) but the dedicated guide was not located. This is the external-approval extension point and worth chasing.

- **Ramp's money transmission structure.** Not public. Whether they operate as agent of payee, under bank partnership, or with own licenses is undetermined.

- **Interchange rate specifics by MCC and card product.** Only blended estimates are public.

- **Physical card fulfillment mechanics** and the card-state enum. The physical cards API reference was not retrieved.

- **`ramp-rate` guide** — likely FX rate handling for cross-border. Not fetched.

- **Item receipts and vendor agreements** field-level schemas. Only their webhook events are documented in what was retrieved.