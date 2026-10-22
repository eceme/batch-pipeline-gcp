# Shortcuts for common commands; run `make check` before pushing.
.PHONY: check test ingest load dbt-debug

check:  ## Same checks as CI: lockfiles, format, lint, tests
	uv lock --check
	uv lock --check --directory dbt
	uv run ruff format .
	uv run ruff check .
	uv run pytest

test:  ## Unit tests only
	uv run pytest -v

ingest:  ## GitHub -> GCS; optional DATE=YYYY-MM-DD
	uv run --env-file .env python -m ingestion.fetch_repos $(if $(DATE),--date $(DATE))

load:  ## GCS -> BigQuery raw.github_repos; optional DATE=YYYY-MM-DD
	uv run --env-file .env python -m ingestion.load_to_bigquery $(if $(DATE),--date $(DATE))

dbt-debug:  ## Check that dbt can connect to BigQuery
	cd dbt && uv run --env-file ../.env dbt debug
