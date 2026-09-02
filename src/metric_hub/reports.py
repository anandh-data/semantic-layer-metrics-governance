from __future__ import annotations

import html
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .drift import DriftResult
from .validation import CheckResult


STYLE = """body{font-family:Inter,Arial,sans-serif;background:#f4f7fb;color:#172033;margin:0}.wrap{max-width:1100px;margin:auto;padding:32px}.hero{background:#14213d;color:white;padding:28px;border-radius:14px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.card{background:white;padding:20px;border-radius:12px;box-shadow:0 2px 12px #dce3ed}.ok{color:#087f5b}.bad{color:#c92a2a}table{width:100%;border-collapse:collapse;background:white}th,td{text-align:left;padding:10px;border-bottom:1px solid #e9ecef}th{background:#edf2ff}@media(max-width:700px){.grid{grid-template-columns:1fr}}"""


def _page(title: str, body: str) -> str:
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>{html.escape(title)}</title><style>{STYLE}</style></head><body><main class='wrap'>{body}</main></body></html>"


def quality_report(checks: list[CheckResult], destination: Path) -> None:
    passed = sum(check.status == "pass" for check in checks)
    rows = "".join(f"<tr><td>{html.escape(c.dataset)}</td><td>{html.escape(c.check)}</td><td class='{'ok' if c.status == 'pass' else 'bad'}'>{c.status.upper()}</td><td>{html.escape(str(c.observed))}</td><td>{html.escape(c.expectation)}</td></tr>" for c in checks)
    body = f"<section class='hero'><h1>Data Quality Report</h1><p>Actual pre-ingestion validation results.</p></section><section class='grid'><div class='card'><h2>{len(checks)}</h2><p>Total checks</p></div><div class='card'><h2 class='ok'>{passed}</h2><p>Passed</p></div><div class='card'><h2 class='bad'>{len(checks)-passed}</h2><p>Failed</p></div></section><table><tr><th>Dataset</th><th>Check</th><th>Status</th><th>Observed</th><th>Expected</th></tr>{rows}</table>"
    destination.write_text(_page("Data Quality Report", body))


def dashboard(daily: pd.DataFrame, drift: list[DriftResult], html_path: Path, image_path: Path) -> None:
    total_revenue = float(daily.net_revenue.sum())
    closed = int(daily.closed_orders.sum())
    avg_turnaround = float(daily.average_turnaround_days.mean())
    drift_rows = "".join(f"<tr><td>{r.team_name}</td><td>${r.governed_value:,.2f}</td><td>${r.reported_value:,.2f}</td><td class='{'ok' if r.status == 'certified' else 'bad'}'>{r.status.upper()}</td></tr>" for r in drift)
    body = f"<section class='hero'><h1>Metric Governance Control Center</h1><p>Certified business metrics and cross-team drift.</p></section><section class='grid'><div class='card'><h2>${total_revenue:,.0f}</h2><p>Governed net revenue</p></div><div class='card'><h2>{closed:,}</h2><p>Closed orders</p></div><div class='card'><h2>{avg_turnaround:.1f} days</h2><p>Average turnaround</p></div></section><h2>Team certification</h2><table><tr><th>Team</th><th>Governed</th><th>Reported</th><th>Status</th></tr>{drift_rows}</table><p>Generated from the executed warehouse mart and drift engine.</p>"
    html_path.write_text(_page("Metric Governance Dashboard", body))
    monthly = daily.assign(metric_date=pd.to_datetime(daily.metric_date)).set_index("metric_date").resample("ME").agg({"net_revenue":"sum","closed_orders":"sum"})
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    fig.suptitle("Metric Governance Control Center", fontsize=20, fontweight="bold")
    axes[0].plot(monthly.index, monthly.net_revenue, color="#3b5bdb", marker="o")
    axes[0].set_title("Governed Net Revenue by Month")
    axes[0].set_ylabel("USD")
    axes[0].grid(alpha=.25)
    labels = [r.team_name for r in drift]
    deltas = [r.absolute_delta for r in drift]
    axes[1].bar(labels, deltas, color=["#2f9e44" if r.status == "certified" else "#e03131" for r in drift])
    axes[1].set_title("Absolute Drift from Governed Net Revenue")
    axes[1].set_ylabel("USD")
    axes[1].grid(axis="y", alpha=.25)
    fig.savefig(image_path, dpi=150)
    plt.close(fig)


def evidence_charts(daily: pd.DataFrame, drift: list[DriftResult], checks: list[CheckResult], screenshot_dir: Path) -> None:
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    monthly = daily.assign(metric_date=pd.to_datetime(daily.metric_date)).set_index("metric_date").resample("ME").net_revenue.sum()
    fig, axis = plt.subplots(figsize=(12, 6), constrained_layout=True)
    axis.plot(monthly.index, monthly.values, color="#364fc7", marker="o", linewidth=2.5)
    axis.set(title="Governed Net Revenue Trend", ylabel="USD", xlabel="Month")
    axis.grid(alpha=.25)
    fig.savefig(screenshot_dir / "revenue-trend.png", dpi=150)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(10, 6), constrained_layout=True)
    axis.bar([r.team_name.title() for r in drift], [r.absolute_delta for r in drift], color=["#2b8a3e" if r.status == "certified" else "#c92a2a" for r in drift])
    axis.set(title="Cross-Team Net Revenue Drift", ylabel="Absolute difference from governed value (USD)")
    axis.grid(axis="y", alpha=.25)
    fig.savefig(screenshot_dir / "metric-drift.png", dpi=150)
    plt.close(fig)

    statuses = pd.Series([c.status for c in checks]).value_counts()
    fig, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    axis.bar(statuses.index.str.title(), statuses.values, color=["#2b8a3e" if value == "pass" else "#c92a2a" for value in statuses.index])
    axis.set(title="Pre-Ingestion Data Quality Gate", ylabel="Checks")
    axis.set_ylim(0, max(statuses.values) + 1)
    fig.savefig(screenshot_dir / "data-quality-summary.png", dpi=150)
    plt.close(fig)
