# Metric catalog

The machine-readable catalog in `registry/metrics.json` is authoritative. It contains 25 governed metrics: 17 mortgage-application measures sourced from public HMDA records and eight title, escrow, and finance measures sourced from the operational model.

Every entry records its business name, owner, version, grain, effective date, calculation, and definition. Approval evidence is stored in `registry/approvals.json`; definition changes are stored in `registry/change-history.json`.

## Corrected definitions

- **Denial rate v2:** denied applications divided by applications with a final credit decision—originated, approved but not accepted, or denied. Withdrawals, incomplete files, purchased loans, and preapproval outcomes are excluded.
- **Net revenue v2:** posted recognized-revenue and refund transactions, replacing the previous order-value estimate.
- **Close rate v2:** closed orders divided by all orders, including cancelled orders in the population.

The superseded and corrected Power BI expressions remain in `bi/` so reviewers can trace each discrepancy and its resolution.
