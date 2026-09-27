# Interview Notes & Proof: Internal Expense Management Framework
**Interviewee:** Muneer, Head of Operations  
**Key Systems:** Excel, Jira, OpenAir  

---

## Executive Summary

During my interview with **Muneer (Head of Operations)**, he detailed his operational framework for managing company internal expenses. Muneer's strategy balances day-to-day administrative speed with strict financial compliance using a three-tool system:

1. **Excel:** Pre-approved quarterly macro-budgeting and master financial models.
2. **Jira:** Workflow requisitions, approval chains, invoice attachments, and audit trails.
3. **OpenAir:** Project-level cost mapping, client billables, and account profitability tracking.

Below is a summary of how Muneer structures, approves, and audits expense workflows across the organization.

---

## Expense Governance Matrix

| Expense Category | Scope & Line Items | Tools Used | Workflow & Approval Mechanism |
| :--- | :--- | :--- | :--- |
| **Fixed Facility & Lease** | Lease, Common Area Maintenance (CAM), Utilities | Excel & Jira | Operates on a pre-approved quarterly budget. Jira tickets are raised for monthly payment routing and invoice verification. |
| **Day-to-Day OPEX** | Office Supplies, Stationery, Routine F&B | Jira & Excel | Requisition ticket raised in Jira; reviewed and approved by Muneer against monthly category thresholds. |
| **Client-Centric Expenses**| Client Gifting, Event Catering, Hospitality | OpenAir & Jira | Pre-cleared by the Client/Account Lead. Tracked in OpenAir under specific client cost centers to manage client budgets. |
| **Project Operations** | Client visits, travel, site setups | Jira & OpenAir | Jira ticket must be mapped to a specific OpenAir Project Code; requires dual sign-off from Project Manager and Muneer. |

---

## Breakdown of Muneer's Operational Process

### 1. Macro Budgeting & Allocation (Quarterly Planning)
Muneer starts every quarter by establishing a baseline budget model in **Excel** alongside executive management. 

* **Fixed Overhead:** Contractual leases, CAM(Common Area Maintenance) charges, and utility projections.
* **Variable OPEX:** Office supplies, stationery, team F&B, and routine maintenance.

Once signed off by management, this Excel master budget serves as the official pre-approved spending limit for the quarter.

### 2. Facility & Overhead Cost Execution
For contractual expenses like lease agreements, CAM fees, and daily utilities:
* Muneer relies on the baseline quarterly approvals in Excel.
* For actual payment processing, his team logs a standardized **Facilities Ticket in Jira** for each invoice.
* Bills and receipts are attached to the ticket, cross-referenced against the master budget, and routed directly to Finance for settlement.

### 3. Day-to-Day Operational Expenses (OPEX)
For routine office supplies, pantry orders, and stationery, Muneer enforces a strict **"ticket-first" policy**:
1. Admin teams or department leads submit a requisition ticket in **Jira**.
2. Muneer reviews the request to verify operational necessity and confirm it fits within the monthly OPEX quota.
3. Vendors are paid only after invoice upload, and digital receipts are mandatory attachments before closing the Jira ticket.
4. At month-end, total spend logged in Jira is reconciled against the Excel baseline.

### 4. Client-Approved & Project-Linked Expenses
To maintain clean P&L accounting and prevent scope creep, Muneer utilizes **OpenAir**:
* **Client Gifting & Hospitality:** Any client entertainment or gift budget must first be cleared by the Account/Client Lead. Requisitions move through Jira but are coded to the specific client ledger in OpenAir.
* **Project Travel & Logistics:** Expenses incurred for client site visits or project setups require a Jira request tied directly to an active **OpenAir Project Code**. This gives Muneer and the project leads real-time visibility into project margin impacts.

---

## Audit, Control & Variance Reconciliation

Muneer emphasized that system integrity relies on consistent auditing:
* **Weekly Reconciliation:** Operations cross-checks active Jira approval tickets against OpenAir expense logs to ensure zero unapproved spend.
* **Monthly Variance Analysis:** Total expenditures in Jira and OpenAir are benchmarked against the primary Excel budget.
* **5% Variance Threshold:** Any category variance exceeding 5% triggers an immediate operational review by Muneer to adjust workflows or recalibrate future budgets.

Through this structured flow, Muneer ensures 100% audit readiness, full receipt tracking, and clear accountability across all internal spending.