"""Reporting utilities for evaluation results."""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict
import json


def write_reports(results: List[Dict], aggregate: Dict, out_dir: Path) -> None:
    """Write JSON and Markdown reports.

    Parameters
    ----------
    results:
        List of per-case dictionaries containing at least ``case_id`` and
        ``metrics``.
    aggregate:
        Dictionary with aggregate metrics.
    out_dir:
        Output directory where ``results.json`` and ``report.md`` will be
        created.
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = {"cases": results, "aggregate": aggregate}
    (out_dir / "results.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = ["| Case | Coverage | Precision@1 | Gaps |", "|------|----------|-------------|------|"]
    for r in results:
        m = r.get("metrics", {})
        gaps = sum(m.get("gap_stats", {}).values())
        lines.append(
            f"| {r.get('case_id')} | {m.get('coverage', 0):.2f} | {m.get('precision_at_1', 0):.2f} | {gaps} |"
        )
    lines.append("")
    agg_line = (
        f"**Aggregate**: coverage={aggregate.get('coverage',0):.2f}, "
        f"precision@1={aggregate.get('precision_at_1',0):.2f}, "
        f"gaps={sum(aggregate.get('gap_stats',{}).values())}"
    )
    lines.append(agg_line)
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
