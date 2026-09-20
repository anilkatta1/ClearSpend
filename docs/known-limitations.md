# Known limitations

- This is a synthetic-data MVP and is not connected to banking, cards, payments, or accounting systems.
- Header-selected demo identities are for the local demonstration only; production requires OIDC and hardened sessions.
- Audit hash linking detects accidental modification but is not an external notarization mechanism.
- PostgreSQL application-level tenant scoping is implemented; Row-Level Security is deferred.
- The fake AI provider is the default. Live model accuracy must be measured before any customer claim.
- Receipt OCR uses Tesseract for images and embedded PDF text. Scanned PDFs without text are marked unreadable; OCR accuracy has not yet been validated on a customer corpus.
- New receipt bytes are encrypted client-side with AES-256-GCM and stored in separate MinIO quarantine/clean buckets. The local key is environment-provided; production still requires a managed KMS, envelope keys per tenant/object, rotation, and secret-manager delivery.
- ClamAV scanning is fail closed and runs before document parsing. Signature-based malware detection and prompt-injection heuristics reduce risk but cannot prove a document safe; production still requires signature-update monitoring, sandboxing for richer formats, red-team cases, and incident procedures.
- Legacy synthetic receipts created before migration remain marked `LEGACY_UNSCANNED` in PostgreSQL. They cannot be used as newly submitted evidence until migrated/re-scanned.
- Automated retention/deletion and short-lived signed object-store access are not implemented. The API decrypts authorized clean objects server-side; quarantined/failed objects are never downloadable.
- CSV `EXPORTED` means an accountant-ready file was generated, not that an ERP accepted it or a reimbursement was paid.
- Expense and audit list endpoints are not yet cursor-paginated and must be bounded before sustained pilot volume.
