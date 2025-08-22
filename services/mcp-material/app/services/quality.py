from __future__ import annotations
from prometheus_client import REGISTRY
from typing import Dict, Any

def collect_metrics_snapshot() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for metric in REGISTRY.collect():
        mname = metric.name
        samples = []
        for s in metric.samples:
            samples.append({
                "name": s.name,
                "labels": s.labels,
                "value": s.value,
            })
        out[mname] = samples
    return out

