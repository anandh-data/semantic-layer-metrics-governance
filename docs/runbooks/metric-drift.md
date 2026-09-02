# Runbook: governed metric drift

1. Confirm the drift is outside both absolute and relative tolerances.
2. Identify the dashboard expression and filter context supplied by the BI adapter.
3. Compare its grain, inclusion rules, and time zone with the registry definition.
4. Check the registry commit and dbt manifest used for the last successful evaluation.
5. Block dashboard certification until the BI calculation is aligned or an approved metric version is introduced.
6. Record owner, root cause, affected reporting periods, and remediation commit in the incident ticket.

Never silently change a governed definition to match a dashboard. Meaning changes require review and a version increment.
