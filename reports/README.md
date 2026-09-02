# Generated reports

| Artifact | Producer | Meaning |
|---|---|---|
| `quality-results.json` | `validation.py` | Machine-readable source checks |
| `data-profile.html` | `profiling.py` | Row, column, type, null, and cardinality profile |
| `data-quality-report.html` | `reports.py` | Human-readable quality evidence |
| `metric-drift-results.json` | `drift.py` | Governed versus team calculations |
| `pipeline-summary.json` | `run_pipeline.py` | Run identity, counts, status, and timestamps |

These artifacts are overwritten on each run so the repository never mixes evidence from different pipeline executions.
