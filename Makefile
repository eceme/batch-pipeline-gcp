# Shortcuts for common commands; run `make check` before pushing.
.PHONY: check test ingest load

check:  ## Same checks as CI: lockfile, format, lint, tests
	uv lock --check
	uv run ruff format .
	uv run ruff check .
	uv run pytest

test:  ## Unit tests only
	uv run pytest -v

ingest:  ## GitHub -> GCS; optional DATE=YYYY-MM-DD
	uv run --env-file .env python -m ingestion.fetch_repos $(if $(DATE),--date $(DATE))

load:  ## GCS -> BigQuery raw.github_repos; optional DATE=YYYY-MM-DD
	uv run --env-file .env python -m ingestion.load_to_bigquery $(if $(DATE),--date $(DATE))
