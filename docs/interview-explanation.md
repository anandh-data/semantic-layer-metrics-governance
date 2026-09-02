# Interview explanation

## Thirty seconds

I built a governed metrics platform for a fictional multi-team transaction business. Finance, Operations, and Commercial calculated net revenue differently. I generated 50,000 orders and their escrow and ledger events, loaded PostgreSQL, transformed the data with dbt, calculated the approved metric, and automatically compared team results. The executed run certified Finance and detected 15.3% and 41.8% drift in the other definitions.

## Engineering depth

- Parquet source data is deterministic and SHA-256 versioned.
- PostgreSQL enforces keys, domains, and relationships.
- dbt produces staged, order-grain, and date-region marts with 15 tests.
- Drift uses metric-specific absolute and relative thresholds.
- JSON/HTML reports and the dashboard are generated from the executed mart.
- Failure injection proves duplicates block publication.

## Trade-off

Purpose-built synthetic data is more appropriate than a public dataset because the project tests conflicting organizational definitions. It is safe to publish and allows expected results to remain reproducible.
