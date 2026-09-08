# Local operations runbook

## Start

```bash
cp .env.example .env
make demo
```

The stack applies Alembic migrations, applies the Procrastinate schema, seeds synthetic tenants and users, then starts API, worker, and web services. Open `http://localhost:3000`; API documentation is at `http://localhost:8000/docs`.

## Health and diagnosis

```bash
docker compose ps
make smoke
docker compose logs --since=10m api worker
```

Every API response includes `X-Correlation-ID`. Supply a known value when reproducing an issue and search structured logs and audit events using it.

## Recovery

- API enqueue failure: leave the committed outbox event unchanged; the worker relay retries it.
- Worker restart: Procrastinate retains queued jobs in PostgreSQL.
- Duplicate delivery: queue locks and the unique assessment-attempt identity make processing idempotent.
- AI failure: the workflow records a fallback and routes the expense to human review.
- Audit mismatch: stop financial decisions for the tenant, preserve database evidence, and investigate before repair.

## Stop

`make down` stops containers and preserves the PostgreSQL volume. To remove the volume, use `docker compose down --volumes` only when synthetic local data may be destroyed.

