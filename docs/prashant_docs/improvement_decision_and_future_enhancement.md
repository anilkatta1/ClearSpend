# ClearSpend: Current Achievements, Improvement Decisions, and Future Enhancements

Reviewed against the project on 27 September 2026.

## 1. What are we achieving in our app?

ClearSpend brings receipt submission, policy assessment, human review, corrections, and an accounting CSV handoff into one application. The current delivery is a local, synthetic-data reimbursement-review MVP. It does not pay employees, operate an ERP, or synchronize Excel, Jira, and OpenAir.

### For employees: simpler submission and correction

- Submit 1–20 same-category receipts as one expense report with one business purpose and one report-level approval.
- Upload JPEG, PNG, or PDF receipts, up to 5 MiB each. Current submissions support INR.
- Review and correct extracted merchant, date, and amount fields before submission. The backend calculates the report total from its lines.
- Respond to reviewer information requests and append missed receipts or replace a bundle through a new revision while retaining previous evidence.

**Achievement:** A structured submission and correction workflow with supporting receipts in one place. Reduced entry effort and fewer follow-up conversations are expected benefits that still need measurement with users.

### For reviewers: evidence-backed decisions

- Inspect receipt lines, policy checks, explanations, and pinned policy citations together.
- Use deterministic checks for objective policy conditions and receipt matching before optional AI assistance.
- Approve, reject, or request information for the complete report. AI recommendations do not make the final decision.
- Route uncertain evidence for human review. A deterministic policy failure produces a rejection recommendation, not an automatic final rejection.

**Achievement:** Reviewers receive a consistent, inspectable basis for their decisions. This does not guarantee invoice authenticity, eliminate fraud, or establish measured review-time savings.

### For accounting: a defined handoff after approval

- Move approved reports to `READY_TO_EXPORT`.
- Require human confirmation of accounting coding before generating a CSV.
- Produce one CSV line per current receipt and record export outcomes, including retryable failures.

**Achievement:** Approval leads to a concrete accounting artifact. `EXPORTED` means a file was generated; it does not mean an ERP accepted the expense or an employee was reimbursed.

### For auditors and operations: traceability and recovery

- Retain receipt revisions, assessment evidence, policy references, human decisions, and export events.
- Apply role and tenant access checks and record hash-linked audit events.
- Encrypt receipt objects, quarantine uploads, and scan with ClamAV before parsing. Only clean receipts are eligible for extraction and authorized preview.
- Use durable jobs, a transactional outbox, idempotency, and concurrency controls to support safe retries and consistent workflow state.
- Expose review/export operating metrics and health checks.

**Achievement:** The reimbursement journey is inspectable and supports recovery from processing failures. These controls do not certify compliance or establish customer-data production readiness.

### Practical example

An employee submits hotel and taxi receipts under one supported shared category. They verify each line, and ClearSpend calculates the total and assesses the evidence. A reviewer requests a missing train receipt; the employee appends it through resubmission. After reassessment and human approval, accounting receives a three-line CSV. Earlier evidence remains available for audit.

**Delivered outcome:** A submission → assessment → human review → correction when needed → accounting CSV journey. Payment execution, ERP posting, and proven customer time savings remain outside the achieved outcome.

## 2. Improvement decisions already implemented

- **One report for related receipts:** Group up to 20 same-category receipts while preserving per-line evidence and one atomic review decision. Mixed categories and partial approvals remain unsupported.
- **Deterministic rules before AI:** Keep objective financial checks reproducible and use bounded AI only as assistance. The fake provider is the default; live-model accuracy is not validated for customer use.
- **Human decision authority:** Keep approval, rejection, and accounting confirmation under human control.
- **Secure and versioned evidence:** Use encrypted quarantine/clean storage, fail-closed scanning, restricted document formats, and retained receipt revisions.
- **Structured corrections:** Support information requests and reassessment rather than overwriting the original evidence.
- **CSV accounting handoff:** Provide an actionable export without claiming payment or accounting-system integration.
- **Durable processing and audit:** Use PostgreSQL-backed jobs, an outbox, retry controls, and audit events to trace material actions.

Implementation references: [as-built architecture](../architecture/as-built-architecture.md), [API](../../services/backend/app/main.py), [report schemas](../../services/backend/app/schemas.py), [assessment graph](../../services/backend/app/graph.py), and [decision log](../decision-log.md).

## 3. How all files in prashant_docs relate to the app

The interview notes describe stakeholder processes, not proof that ClearSpend implements those processes or that the interviewees validated the application.

### Muneer_Interview.md — Operations expense management

**Source:** [Operations interview](Muneer_Interview.md) describes Excel budgets, Jira requisitions, OpenAir project mapping, dual approvals, and periodic reconciliation, including a 5% variance threshold.

**Available:** Receipt-backed reimbursement reports, category and purpose fields, deterministic policy checks, human review, correction requests, audit history, and accounting CSV generation.

**Future enhancement:** Project/cost-center mapping, staged approvals, cumulative budget tracking, variance alerts, and integrations with the actual system of record. Current policy amount limits are not a budget ledger, and current metrics do not calculate project profitability or the interview's budget variance.

### Employee_Logistics_reimbersment.md — Relocation reimbursement

**Source:** [Relocation notes](Employee_Logistics_reimbersment.md) describe employee-specific pre-approved limits, approved vendors, HR approval evidence, and multiple approval stages before payment.

**Available:** The general receipt submission, multi-receipt report, policy assessment, information-request, human review, and CSV handoff capabilities can demonstrate the common reimbursement steps.

**Future enhancement:** Dedicated relocation eligibility, offer-linked entitlements, approved-vendor validation, supporting pre-approval documents, and HR/operations/finance routing. The app does not currently verify relocation eligibility, prove payment, or disburse reimbursements.

### Babul_Interview.md — IT procurement

**Source:** [IT procurement interview](Babul_Interview.md) describes purchase requests, quotations, purchase orders, delivery inspection, and debit/credit note reconciliation.

**Available:** Secure receipt handling, evidence review, human decisions, and audit history exist for reimbursements. They are reusable control patterns, not a delivered procurement module.

**Future enhancement:** Separately scope purchase requisitions, vendor quote comparison, PO/invoice/delivery matching, asset tracking, and debit/credit note reconciliation. These are not current ClearSpend features.

### ai-collaboration-disclosure-interview.md — Documentation disclosure

**Source:** [AI collaboration disclosure](ai-collaboration-disclosure-interview.md) describes human-provided interview knowledge and AI assistance with documentation structure and wording.

**Relevance:** It explains document preparation, not an application feature. Separately, the application retains human authority over verified receipt fields and final review decisions while bounding AI assistance.

**Follow-up:** The author must complete the existing `[Your Name]` and `[Insert Date]` placeholders and verify the declarations. This repository review does not independently attest to interview authenticity or author sign-off.

### improvement_decision_and_future_enhancement.md — This document

This file connects all four supporting documents to current implementation, delivered outcomes, and proposed improvements. Interview-described processes are not classified as implemented without code and verification evidence.

## 4. Transition to an integrated ERP system

**Status: future proposal; not implemented.**

ClearSpend currently integrates its own reimbursement workflow and provides a CSV for downstream accounting. It does not implement ERP budget management, asset management, purchase requisitions, a general ledger, historical data migration, or synchronization with Jira/OpenAir/Excel.

The broader ERP roadmap remains a discovery option based on the interviews:

- **Budget management:** Evaluate moving spreadsheet budgets into a suitable system with cumulative spend tracking and variance visibility.
- **Procure-to-pay routing:** Define and validate purchase-request approval stages and notification requirements before selecting or configuring a system.
- **Asset management:** Separately scope purchase, delivery, inventory, depreciation, and retirement records.
- **Policy controls:** Define versioned, explainable rules and exception handling. Current ClearSpend generates recommendations and preserves human review; it does not automatically issue final rejections for policy failures.

Start by validating the customer's system of record and required accounting fields. A narrow connector would need idempotent delivery, acknowledgements, retries, and reconciliation. A full ERP transition would additionally need migration mapping, data cleanup, access design, financial validation, and a tested cutover plan. No ERP vendor has been selected or integrated by the current project.

## 5. Prioritized future enhancements

### P0 — Before customer-data use

- Implement production identity with OIDC, hardened sessions, and MFA; add database Row-Level Security as defense in depth. Verify production cannot authenticate using demo headers and test cross-tenant denial.
- Add managed encryption keys, rotation, secret delivery, and automated retention/deletion. Demonstrate key rotation and approved data lifecycle behavior.
- Establish TLS, backup/restore testing, scanner-signature monitoring, alert ownership, incident response, and rollback procedures. Record recovery exercises before a customer-data pilot.

### P1 — Improve the current reimbursement journey

- Benchmark OCR on an authorized representative receipt corpus and evaluate bounded OCR for scanned PDFs. Currently, PDFs without embedded text remain unreadable. Preserve employee confirmation and scan-before-parse controls.
- Add browser-driven tests for upload, correction, review, resubmission, export, permissions, and failure paths.
- Add cursor pagination to report/audit lists and validate reviewer queue filtering. Check stable navigation and bounded responses under concurrent inserts.
- Measure submission effort, reviewer handling time, correction cycles, and CSV usability against an agreed baseline. Report sample sizes and failures; do not present synthetic metrics as customer savings.

### P2 — Validate interview-driven extensions

- Add project/cost-center coding only after finance confirms the dimensions and export requirements.
- Design staged approvals with delegation, escalation, separation of duties, and audited transitions.
- Validate relocation entitlements, vendor eligibility, and supporting approval evidence.
- Evaluate mixed-category reports and partial decisions, defining policy and export semantics first.
- Evaluate deduplicated notifications and reminders with appropriate recipient access and limited sensitive content.

### P3 — Broader systems and separate modules

- Build an accounting connector only after choosing the actual receiving system; distinguish file generation, delivery, and confirmed acceptance.
- Prioritize multi-currency, mileage, GST fields, and cumulative budgets from user evidence and explicit business rules.
- Treat ERP transition, procurement, and asset management as separately scoped initiatives.
- Keep payment execution outside the current product; any future proposal needs a separate authorization and reconciliation design.

## 6. Evidence and validation boundary

This document was updated through repository review; application tests were not rerun for this documentation change. Existing verification covers backend tests, frontend checks, and an API/worker smoke journey. Browser-driven coverage remains a gap.

See the [verification guide](../engineering/verification.md), [smoke journey](../../scripts/smoke.py), [release response](../product/ramp-release-response.md), and [known limitations](../known-limitations.md). Mark an enhancement as implemented only when code, verification evidence, and documentation support it.
