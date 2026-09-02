from __future__ import annotations

import html
from pathlib import Path

import pandas as pd


def profile_parquet(paths: list[Path], destination: Path) -> None:
    sections = []
    for path in paths:
        frame = pd.read_parquet(path)
        fields = []
        for column in frame.columns:
            series = frame[column]
            fields.append(
                f"<tr><td>{html.escape(str(column))}</td><td>{html.escape(str(series.dtype))}</td>"
                f"<td>{int(series.isna().sum()):,}</td><td>{int(series.nunique(dropna=True)):,}</td></tr>"
            )
        sections.append(
            f"<section><h2>{html.escape(path.name)}</h2><p>{len(frame):,} rows × {len(frame.columns)} columns; "
            f"{path.stat().st_size:,} bytes.</p><table><tr><th>Column</th><th>Type</th><th>Nulls</th><th>Distinct</th></tr>{''.join(fields)}</table></section>"
        )
    style = "body{font-family:Arial;background:#f5f7fb;color:#172033;max-width:1100px;margin:30px auto}section{background:white;padding:22px;margin:18px 0;border-radius:12px}table{width:100%;border-collapse:collapse}th,td{padding:9px;border-bottom:1px solid #ddd;text-align:left}th{background:#edf2ff}"
    destination.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>Data Profile</title><style>{style}</style></head><body><h1>Executed Dataset Profile</h1>{''.join(sections)}</body></html>")
