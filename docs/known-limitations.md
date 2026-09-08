# Known limitations

- This is a synthetic-data MVP and is not connected to banking, cards, payments, or accounting systems.
- Header-selected demo identities are for the local demonstration only; production requires OIDC and hardened sessions.
- Audit hash linking detects accidental modification but is not an external notarization mechanism.
- PostgreSQL application-level tenant scoping is implemented; Row-Level Security is deferred.
- The fake AI provider is the default. Live model accuracy must be measured before any customer claim.
- Receipt binary storage and OCR are represented by verified metadata in the MVP.
