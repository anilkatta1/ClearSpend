# ADR 0005: Receipt evidence and accounting handoff

- Status: accepted for the synthetic MVP
- Date: 2026-09-15

## Context

Review approval alone does not complete an accountant's job. The MVP must begin with evidence and end in a useful system-of-record handoff without expanding into regulated money movement.

## Decision

Claims begin with a bounded JPEG, PNG, or PDF upload. Open-source Tesseract extracts image text and pypdf extracts embedded PDF text. Extraction only proposes editable fields; deterministic code compares the confirmed amount, currency, merchant, and incurred date and routes unreadable or mismatched evidence to review.

Approval transitions a claim to `READY_TO_EXPORT`. A reviewer or admin confirms account code and cost center, after which ClearSpend creates an auditable CSV export and transitions to `EXPORTED`. Export never means paid.

For the local synthetic MVP, receipt bytes are private application data in PostgreSQL. A customer-data deployment must replace this adapter with encrypted private object storage, malware scanning, retention/deletion controls, and signed access.

## Consequences

The demonstrated workflow is complete from receipt to accountant-ready record while staying outside payouts, bank data, ERP credentials, and ledger scope. OCR uncertainty remains visible and cannot produce an automatic financial decision.
