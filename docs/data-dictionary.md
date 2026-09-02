# Data dictionary

The dataset represents a fictional multi-team transaction business. It is synthetic by design: no FNF records, customer data, or proprietary definitions are used.

| Entity | Grain | Key | Purpose |
|---|---|---|---|
| orders | One row per order | order_id | Lifecycle, region, and transaction value |
| escrow_events | One row per lifecycle event | event_id | Independently recorded operational milestones |
| finance_transactions | One row per ledger event | transaction_id | Recognized revenue rather than order face value |
| fct_order_performance | One row per order | order_id | Governed lifecycle and financial facts |
| metric_daily_performance | Date and region | metric_date, region | BI-ready governed metrics |

`net_revenue` is recognized finance transaction amount for closed orders. `average_turnaround_days` is the elapsed calendar days between open and close, excluding open/cancelled orders.
