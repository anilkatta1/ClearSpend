# ADR 0005: Receipt evidence and accounting handoff

- Status: accepted for the synthetic MVP
- Date: 2026-09-15

## Context

Review approval alone does not complete an accountant's job. The MVP must begin with evidence and end in a useful system-of-record handoff without expanding into regulated money movement.

## Decision

Claims begin with a bounded JPEG, PNG, or PDF upload. Open-source Tesseract extracts image text and pypdf extracts embedded PDF text. Extraction only proposes editable fields; deterministic code compares the confirmed amount, currency, merchant, and incurred date and routes unreadable or mismatched evidence to review.

Approval transitions a claim to `READY_TO_EXPORT`. A reviewer or admin confirms account code and cost center, after which ClearSpend creates an auditable CSV export and transitions to `EXPORTED`. Export never means paid.

Receipt bytes are encrypted with AES-256-GCM before they enter private MinIO quarantine. A separate ClamAV service scans the raw upload before any image/PDF parser runs. Deep validation rejects malformed, oversized, multi-frame, encrypted, active-content, or embedded-file documents; only clean objects are promoted and decryptable through the authorized API. Replacement evidence creates a new immutable `expense_receipts` revision while retaining the superseded hash and actor/time trail. Customer-data deployment still requires managed KMS/envelope keys, OIDC, retention/deletion, signature monitoring, and signed access where needed.

## Consequences

The demonstrated workflow is complete from quarantined receipt to accountant-ready record while staying outside payouts, bank data, ERP credentials, and ledger scope. OCR uncertainty, unsafe content, and prompt-injection signals remain visible and cannot produce an automatic financial decision. The extra MinIO and ClamAV services increase startup time and operations burden in exchange for an auditable security boundary.
