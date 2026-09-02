# Metric catalog

## Net revenue v1

- Owner: Finance Analytics
- Grain: metric date and region
- Definition: recognized revenue ledger events plus posted refund events for canonically closed orders
- Excludes: open/cancelled order value and unposted estimates
- Source: `raw.finance_transactions`
- dbt output: `analytics.metric_daily_performance.net_revenue`

## Closed orders v1

- Owner: Operations Analytics
- Grain: close date and region
- Definition: count of orders whose canonical status is `closed`
- Excludes: open and cancelled orders
- Source: `raw.orders`

## Average turnaround days v1

- Owner: Escrow Operations
- Grain: close date and region
- Definition: average calendar days from opened date through closed date
- Excludes: open and cancelled orders
- Null policy: no value is published when there are no closed orders

Meaning or grain changes require a new major definition. Corrections retain an audit note and a reproducible backfill plan.
