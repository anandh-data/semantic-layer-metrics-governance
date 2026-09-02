# Architecture and governance workflow

The version-controlled registry is the source of truth. A restricted expression evaluator computes metrics from aggregated facts; a BI export adapter supplies independently reported values; the comparator raises drift when absolute or relative tolerance is exceeded.

In production, dbt/MetricFlow or Cube compiles definitions into warehouse SQL. Pull requests require an owner, version increment, description, and impact review. Power BI exports are checked on a schedule and alerts link back to the definition and owner.

## Change policy

1. Additive metric: minor registry release.
2. Corrected logic with same meaning: patch release and backfill note.
3. Meaning or grain change: new metric name or major version; never silently overwrite history.
