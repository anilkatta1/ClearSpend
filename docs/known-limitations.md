# Known limitations

- This is a synthetic-data MVP and is not connected to banking, cards, payments, or accounting systems.
- Header-selected demo identities are for the local demonstration only; production requires OIDC and hardened sessions.
- Audit hash linking detects accidental modification but is not an external notarization mechanism.
- PostgreSQL application-level tenant scoping is implemented; Row-Level Security is deferred.
- The fake AI provider is the default. Live model accuracy must be measured before any customer claim.
- Receipt OCR uses Tesseract for images and embedded PDF text. Scanned PDFs without text are marked unreadable; OCR accuracy has not yet been validated on a customer corpus.
- Receipt bytes are stored privately in PostgreSQL for the synthetic local MVP. Customer data requires encrypted object storage, malware scanning, retention/deletion, and signed access.
- CSV `EXPORTED` means an accountant-ready file was generated, not that an ERP accepted it or a reimbursement was paid.
- Expense and audit list endpoints are not yet cursor-paginated and must be bounded before sustained pilot volume.
