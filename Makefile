.PHONY: setup demo dev down migrate seed test test-backend test-frontend lint verify smoke logs

setup:
	uv sync --directory services/backend --all-extras
	pnpm --dir apps/web install

demo:
	docker compose up --build

dev: demo

down:
	docker compose down

migrate:
	docker compose run --rm api alembic upgrade head

seed:
	docker compose run --rm api python -m app.seed

test: test-backend test-frontend

test-backend:
	services/backend/.venv/bin/pytest services/backend/tests

test-frontend:
	pnpm --dir apps/web test

lint:
	services/backend/.venv/bin/ruff check services/backend/app services/backend/tests
	services/backend/.venv/bin/mypy services/backend/app
	pnpm --dir apps/web lint
	pnpm --dir apps/web typecheck

verify: lint test
	docker compose config --quiet

smoke:
	curl --fail --silent http://localhost:8000/health/ready
	curl --fail --silent http://localhost:3000 >/dev/null
	services/backend/.venv/bin/python scripts/smoke.py

logs:
	docker compose logs -f api worker web
