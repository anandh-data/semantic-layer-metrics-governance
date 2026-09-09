# Project data

The committed evidence was generated from real public mortgage data and deterministic fictional operational data.

| File | Role |
|---|---|
| `raw/orders.parquet` | 50,000 canonical orders |
| `raw/escrow_events.parquet` | Lifecycle events independently recorded by escrow operations |
| `raw/finance_transactions.parquet` | Recognized revenue and refund ledger events |
| `raw/hmda_applications.parquet` | 2.8M-record analytical sample from the CFPB 2017 nationwide HMDA file; generated locally and ignored by Git |
| `processed/daily-governed-metrics.parquet` | dbt-produced, BI-ready governed mart export |
| `processed/order-performance.parquet` | dbt-produced order-grain governed fact export |
| `manifests/raw-data-manifest.json` | Row counts, file sizes, SHA-256 hashes, seed, and version |
| `manifests/hmda-data-manifest.json` | Official URL, record counts, selection rule, columns, and SHA-256 hashes |

The HMDA source is public and privacy-modified by the CFPB. All operational identities are fictional; there is no employer or customer data. Follow `docs/hmda-source.md`, run `make hmda`, and then run `make pipeline`.
