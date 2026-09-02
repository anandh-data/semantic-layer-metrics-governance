# Execution evidence

`end-to-end-pipeline.jsonl` is structured output from the successful committed pipeline run. `dbt-build.log` is the captured stdout/stderr of the real dbt build against local PostgreSQL.

Logs are intentionally bounded and sanitized. Local database files, credentials, terminal history, and unrestricted runtime logs are excluded. Regenerate both files with `make pipeline`.
