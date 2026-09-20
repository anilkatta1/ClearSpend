# Local operations runbook

## Start

```bash
cp .env.example .env
make demo
```

The stack applies Alembic migrations, applies the Procrastinate schema, seeds synthetic tenants and users, then starts PostgreSQL, MinIO, ClamAV, API, worker, and web services. On first start, ClamAV may need time to download signatures. Open `http://localhost:3000`; API documentation is at `http://localhost:8000/docs`.

## Health and diagnosis

```bash
docker compose ps
make smoke
docker compose logs --since=10m api worker minio clamav
```

Every API response includes `X-Correlation-ID`. Supply a known value when reproducing an issue and search structured logs and audit events using it.

## Recovery

- API enqueue failure: leave the committed outbox event unchanged; the worker relay retries it.
- Worker restart: Procrastinate retains queued jobs in PostgreSQL.
- Duplicate delivery: queue locks and the unique assessment-attempt identity make processing idempotent.
- AI failure: the workflow records a fallback and routes the expense to human review.
- Object storage failure: readiness fails; upload returns a retryable service error and does not claim success.
- Malware scanner failure: readiness fails and receipt scanning fails closed; never bypass scanning to restore availability.
- Infected or structurally unsafe receipt: it remains encrypted in quarantine, is marked blocked, and cannot be previewed or submitted.
- Encryption failure or invalid authentication tag: do not return bytes; preserve identifiers/audit evidence and investigate key/object integrity.
- Audit mismatch: stop financial decisions for the tenant, preserve database evidence, and investigate before repair.

## Receipt security configuration

- `RECEIPT_ENCRYPTION_KEY` is a base64-encoded 32-byte local-development key. Never reuse the example key for real data.
- `RECEIPT_QUARANTINE_BUCKET` and `RECEIPT_CLEAN_BUCKET` must remain private.
- `MALWARE_SCAN_REQUIRED=true` is the normal mode. Disabling it is only acceptable for isolated unit tests with synthetic bytes.
- Readiness requires PostgreSQL, both receipt buckets, and ClamAV. Check `docker compose ps` and scanner logs before a demo.

## Stop

`make down` stops containers and preserves the PostgreSQL volume. To remove the volume, use `docker compose down --volumes` only when synthetic local data may be destroyed.
