# batch-pipeline-gcp

Batch data pipeline on GCP: GitHub REST API → Python ingestion → GCS → BigQuery → dbt → Airflow.
Infrastructure is managed with Terraform.

## Working conventions

- Explain the rationale behind non-obvious design choices, briefly (in chat, not in code).
- Code comments: at most one short sentence, only where the "why" is not obvious. No comment blocks.
- Review changes critically: flag bugs, security issues and non-idiomatic patterns.
- Everything in the repo is in English: code, comments, commit messages, docs, file names. No other language, even though the maintainer may chat in another one.
- Never run `terraform apply` or `terraform destroy`. Run `terraform plan` and show the output instead.
- **The GitHub repo is public.** Never commit secrets, tokens, credentials, state or plan files; check every diff for them before committing.
- **Keep GCP costs near zero.** Prefer free-tier usage; flag any resource or setting that would add a recurring cost before adding it.
- **Docs are for other people to reproduce the project.** README and other Markdown files use clean, beginner-friendly English, with tables and diagrams where they help.

## Architecture

- Source: GitHub REST API — repository metadata (SCD2 dimension) and daily star/fork counts (periodic snapshot fact).
- Raw layer: JSON files in a GCS bucket, partitioned by date (`raw/github/dt=YYYY-MM-DD/`).
- Warehouse: BigQuery datasets `raw`, `staging`, `marts`; loaded with load jobs, never streaming inserts.
- Transformations: dbt (staging models → star schema in marts; snapshots for SCD2; incremental facts).
- Orchestration: Airflow running locally with Docker Compose.

## Decisions (discuss before changing)

- **No service account key files.** Local tooling uses Application Default Credentials; the pipeline service account is used via impersonation.
- Two identities: a human account deploys infrastructure; `pipeline-sa` (created by Terraform) runs the pipeline with least-privilege roles granted at the narrowest scope (project / dataset / bucket).
- Location: `EU` multi-region for both GCS and BigQuery (must match for load jobs).
- Cost controls: GCS lifecycle rule deletes raw files after 30 days; no managed compute (Composer, Dataproc) — heavy tooling runs locally.
- `force_destroy` / `delete_contents_on_destroy = true`: the whole stack must be removable with `terraform destroy`.
- Terraform layout: `versions.tf`, `providers.tf`, `variables.tf`, `terraform.tfvars` (git-ignored; `terraform.tfvars.example` is committed), `storage.tf`, `bigquery.tf`, `iam.tf`, `outputs.tf`. No modules (single environment, small footprint).
- Commit `.terraform.lock.hcl`; never commit state files, `.env`, or `*.json` credentials.

## Common commands

```bash
cd terraform && terraform fmt && terraform validate && terraform plan
uv run ruff format . && uv run ruff check .        # Python format + lint (same checks as CI)
uv run --env-file .env python -m ingestion.fetch_repos [--date YYYY-MM-DD]   # GitHub → GCS
```

## Roadmap

1. Terraform: bucket, datasets, service account
2. Ingestion: GitHub API → GCS → BigQuery load job (idempotent)
3. dbt: staging, star schema, SCD2 snapshot, incremental fact, tests
4. Airflow: daily DAG, retries, backfill
5. Data quality checks, README with architecture diagram and trade-offs
