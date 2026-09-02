# Semantic Layer & Metric Governance Hub

[![CI](https://github.com/anandh-analytics/semantic-metric-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/anandh-analytics/semantic-metric-governance/actions)

A governed KPI registry plus an executable drift gate for the recurring business problem: **Finance and Marketing report different revenue from the same company data.**

## Demo

```bash
make test
make demo
```

The included BI extract deliberately reports gross sales as net revenue. The command prints the governed value, reported value, delta, and a drift flag, then exits non-zero. `make demo` treats that expected detection as success.

## Design

- `registry/metrics.json`: definitions, owners, versions, and business meaning
- `src/metric_hub`: safe expression evaluation, source aggregation, drift comparison
- `sample_data`: reproducible facts and an intentionally incorrect BI export
- `docs/architecture.md`: release rules and production evolution

## Why a registry instead of dashboard-local DAX?

Central definitions are reviewable, versioned, testable, and reusable. Dashboard-local formulas optimize for convenience but create invisible forks. The local evaluator makes the concept runnable without a warehouse; dbt Semantic Layer/MetricFlow is the documented production adapter.

## Interview discussion points

- Metric ownership and change approval across Finance, Marketing, and Operations
- Backward compatibility when definition meaning or grain changes
- Relative versus absolute drift thresholds
- Why a semantic layer complements rather than replaces BI tooling

## License

MIT
