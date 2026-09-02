# Project data

These files are the actual deterministic dataset used by the committed pipeline run, not reduced illustrative fixtures.

| File | Role |
|---|---|
| `raw/orders.parquet` | 50,000 canonical orders |
| `raw/escrow_events.parquet` | Lifecycle events independently recorded by escrow operations |
| `raw/finance_transactions.parquet` | Recognized revenue and refund ledger events |
| `processed/daily-governed-metrics.parquet` | dbt-produced, BI-ready governed mart export |
| `processed/order-performance.parquet` | dbt-produced order-grain governed fact export |
| `manifests/raw-data-manifest.json` | Row counts, file sizes, SHA-256 hashes, seed, and version |

All identities are fictional and there is no customer or employer data. Reproduce the exact raw files with `make pipeline`; seed `2026` and row count `50000` are fixed in the committed run.
