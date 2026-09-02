# Testing strategy

## Unit tests

Exercise safe expression parsing, threshold behavior, deterministic generation, relational consistency, zero baselines, and invalid input rejection.

## Failure injection

Introduce duplicate business keys and confirm the pre-ingestion quality gate blocks publication.

## Integration tests

Connect to the executed PostgreSQL warehouse, compare raw and mart row counts, and assert referential integrity.

## dbt tests

Run 15 source/model checks: uniqueness, non-nullness, relationships, accepted domains, and nonnegative turnaround.

## End-to-end evidence

Confirm the committed run processed 50,000 orders, completed without quality failures, and produced nonempty dashboard/report artifacts.

Commands:

```bash
make test
make local-db-start
make integration-test
make pipeline
```
