"""Computation of quality metrics for evaluation cases."""
from __future__ import annotations

from typing import Dict, List

from .dataset import EvalCase


def compute_case_metrics(case: EvalCase, priced_bom: Dict) -> Dict:
    """Compute metrics for a single evaluation case."""
    expected = case.expected_items
    total = len(expected)
    priced_items = priced_bom.get("items") or []
    gaps = priced_bom.get("gaps") or []

    coverage = len(priced_items) / total if total else 0.0

    # Mock precision@1: compare first N priced items to expected items in order
    correct = 0
    for i, exp in enumerate(expected):
        if i < len(priced_items) and priced_items[i].get("name") == exp.get("name"):
            correct += 1
    precision_at_1 = correct / total if total else 0.0

    gap_stats: Dict[str, int] = {}
    for g in gaps:
        reason = g.get("reason", "unknown")
        gap_stats[reason] = gap_stats.get(reason, 0) + 1

    return {
        "case_id": case.id,
        "coverage": coverage,
        "precision_at_1": precision_at_1,
        "gap_stats": gap_stats,
    }


def aggregate_metrics(case_metrics: List[Dict]) -> Dict:
    """Aggregate metrics across cases."""
    if not case_metrics:
        return {"coverage": 0.0, "precision_at_1": 0.0, "gap_stats": {}}
    agg = {"coverage": 0.0, "precision_at_1": 0.0, "gap_stats": {}}
    for m in case_metrics:
        agg["coverage"] += m.get("coverage", 0.0)
        agg["precision_at_1"] += m.get("precision_at_1", 0.0)
        for k, v in m.get("gap_stats", {}).items():
            agg["gap_stats"][k] = agg["gap_stats"].get(k, 0) + v
    n = len(case_metrics)
    agg["coverage"] /= n
    agg["precision_at_1"] /= n
    return agg
