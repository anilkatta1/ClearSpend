# 01 — Product Surface Area

The complete module inventory, assembled from Ramp's marketing site, developer documentation, and Contrary Research's business breakdown. This is the scope of "full platform."

## Module map

### 1. Corporate Cards

The anchor product. A **charge card**, not a credit card — balances are paid in full on a cycle, so there is no revolving interest, no late fees, and a materially different regulatory posture.

- Physical and virtual Visa cards. Historically one active physical card per user, unlimited virtual cards.

- Cards accepted in 200+ countries; local issuance in 33 countries.

- Wallet provisioning (Apple Pay / Google Pay).

- 3D Secure enrollment for online and international use.

- Spend controls: merchant lock, category lock, country restriction, amount limit, interval (daily / monthly / total / annual), auto-lock date.

- Shared funds — one budget pooled across multiple members, with per-user transaction attribution preserved.

- **Agent Cards** — a merchant-and-amount-scoped credential minted immediately before a single agent-driven checkout. Explicitly not for subscriptions or later merchant charges.

- 1.5% flat unlimited cashback. Notably no points program — a deliberate positioning choice.

- Stablecoin-backed cards for cross-border spend, via a Stripe partnership announced May 2025.

### 2. Expense Management

- Receipt capture via mobile app, SMS, email, Slack, Microsoft Teams, web.

- OCR extraction of merchant, date, amount, line items.

- Auto-verification: a receipt passes if 2 of 3 fields (amount, date, merchant) match the transaction.

- Auto-generated digital receipts for transactions under $75, sourced from POS data — $75 being the IRS substantiation threshold.

- Email integrations (Gmail, Outlook) plus merchant-direct feeds (Amazon Business, Uber, Lyft) for automatic receipt ingestion.

- Real-time policy enforcement, automated reminders, auto-repayment requests, and card locks on sustained non-compliance.

- Nested, conditional approval chains.

### 3. Reimbursements

- Out-of-pocket employee expenses, plus a dedicated mileage path.

- Two directions: `BUSINESS_TO_USER` (default) and `USER_TO_BUSINESS` for amounts an employee owes back.

- Multi-currency: the original expense currency and the payout currency can differ, tracked in separate fields.

- Gated by funds when no card is involved — the same budget primitive constrains reimbursable categories and amounts.

### 4. Accounts Payable / Bill Pay

Launched October 2021.

- Invoice ingestion with OCR extraction into a draft bill.

- Approval routing, GL coding, and payment in one object — payments are nested on the bill rather than exposed as an independent resource.

- Rails: card (earns cashback), ACH, same-day ACH, check, domestic wire, SWIFT international, and stablecoin payout to a vendor wallet.

- Cross-border payments across 190+ countries.

- Two-way accounting sync on bill creation, update, and payment.

- Vendor W-9 storage and export for 1099 support.

- **Ramp Flex** — deferred bill payment at 30/60/90 days. This is a working-capital product and a distinct credit exposure from the card.

### 5. Procurement

Expanded via the August 2023 acquisition of Venue, an AI procurement startup. Gated to the paid tier.

- Custom intake forms with conditional logic, mapped to purchase order fields.

- Dynamic approval routing.

- Purchase order generation, and one-time virtual cards issued against approved POs.

- Invoice-to-PO matching with automatic exact matching, suggested matching otherwise, cascading down to line-item level.

- Two-way and three-way matching (PO / invoice / item receipt). Discrepancies block payment until resolved.

- Vendor agreements with contract parsing — extracting contract amount, payment frequency, start and end dates — and renewal milestone reminders.

- **Seat Intelligence** — SaaS seat usage versus billed seats, via an Okta integration.

### 6. Travel

Launched February 2022.

- Book-anywhere model: the card transaction itself is the policy enforcement point, rather than forcing bookings through a proprietary booking tool.

- Policy controls: maximum airfare and hotel rates, cabin class by flight duration, advance-booking windows, per diem limits.

- Hotel rate monitoring with automatic rebooking.

- Travel dashboard with map, metrics, and trips views. Car rental added April 2025.

- Managed-travel partnerships (Melon, TravelPerk) rather than building a full TMC.

### 7. Banking & Treasury

Launched January 2025. US-only.

Three account types, exposed in the API as an `account_type` enum:

| Enum | Product | Notes |

|---|---|---|

| `WALLET_ACCOUNT` | Checking Account | Operating cash. Multiple permitted per business. |

| `BROKERAGE_ACCOUNT` | Investment Account | Self-directed money market. Max one per entity. |

| `MANAGED_PORTFOLIO_ACCOUNT` | Managed Portfolio | Fixed-income, managed by Moment Advisors. Limited release. |

Deposits sit with First Internet Bank of Indiana for FDIC insurance; brokerage via Apex Clearing. Card spend and outbound bill payments draw from the checking account when it is the funding source. Auto top-up available.

### 8. Accounting Automation

- Native ERP integrations: QuickBooks, QuickBooks Desktop, Xero, NetSuite, Sage Intacct, Workday, Oracle.

- Universal CSV for unsupported providers.

- An open accounting API so third parties can build connectors to any ERP.

- GL auto-coding, custom dimension fields, multi-entity support, bidirectional sync.

### 9. Ramp Intelligence / AI Agents

- **Policy Agent** — reviews 100% of expense submissions in real time, approving compliant spend and flagging exceptions.

- Auto-categorization and GL code assignment, learning from user corrections.

- Fraud detection, invoice transcription, three-way matching.

- **Price Intelligence** — benchmarks vendor pricing against aggregated Ramp transaction data, with LLM analysis on top.

- **Ramp MCP server** at `mcp.ramp.com/mcp` (demo at `demo-mcp.ramp.com/mcp`), plus a CLI, so external AI assistants can operate the platform.

- **AI Spend tracking** — endpoints for AI API keys, teams, and token usage, with an inbound `POST /developer/v1/ai-usage/unified` endpoint for platforms to broadcast usage. Ramp is building a product around metering its customers' own LLM spend.

### 10. Vendor Management

- Centralized vendor records linking card transactions and bill payments to one payee view.

- Document storage (contracts, W-9s, payment instructions).

- Vendor owners for accountability assignment; bulk CSV upload.

### 11. Savings & Insights

- Duplicate and unused subscription detection.

- Unused partner reward detection.

- Negotiation-as-a-service, from the August 2021 Buyer acquisition.

### 12. Platform & Admin

- 200+ to 1,000+ integrations depending on how you count (Gusto, Slack, Teams, Okta, 1Password, Google SSO).

- User roles and multi-entity permission restrictions.

- Audit log with an events API.

- Business incorporation flow (`incorporation:read` / `incorporation:write` scopes exist) — Ramp will incorporate the company for you.

- A financing application flow for onboarding, with `RAMP_SUITE` and `BILL_PAY_ONLY` application types.

- App Center for third-party partner distribution.

## Business model — why the surface is shaped this way

Understanding the monetization explains the architecture, so it belongs here even in a technical dossier.

Approximate revenue mix as reported by third parties: **~70% card interchange, ~15% software subscription, remainder from treasury yield and payment fees.** Ramp collects roughly 250 bps of interchange on a transaction, passes roughly 200 bps to the issuing bank, and keeps roughly **50 bps**. Reported scale: >$1B annualized revenue on >$100B annual purchase volume, 50,000+ customers, valuations reported from $32B (Nov 2025) to $44B.

Three architectural consequences follow directly:

1. **Card volume is the revenue engine, so card-adjacent features are given away free.** The base tier has no subscription fee. Software exists to drive card share of wallet. If you clone this, your free tier is a customer-acquisition cost funded by interchange, and you must model interchange revenue per customer against cost-to-serve before you give anything away.

2. **Take rate compresses as you succeed.** Larger customers negotiate lower rates, and more spend migrates to ACH and bill pay rails that carry almost no interchange. Revenue growth has to come from volume outrunning rate compression, plus subscription and treasury attach. Your financial model must assume declining bps.

3. **Every non-card rail is a cost center that exists to defend the card.** Bill Pay, reimbursements, and treasury monetize weakly or not at all directly. They are there so that finance teams consolidate onto one platform and route more card volume through it. Do not build them expecting direct margin.

## Competitive context

- **Cards:** American Express, Brex, Mercury, Spendesk, Rho, Extend.

- **Expense:** SAP Concur, Expensify, Airbase (acquired by Paylocity, Sept 2024, $325M).

- **AP:** BILL, AvidXchange, Stampli. BILL is the strongest incumbent in invoice automation with real network effects.

- **Travel:** Navan, TravelPerk.

The strategic read: the corporate card market is saturated with well-capitalized players and the *card* is not defensible. Consolidation of the whole finance stack onto one ledger is the defensible position, which is precisely why "full platform" is the only viable clone scope — and also why it is a multi-year build.