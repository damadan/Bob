"""CLI entrypoint for evaluation pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Dict

from fastapi.testclient import TestClient

from .dataset import load_dataset, EvalCase
from .runner import run_cases
from .metrics import compute_case_metrics, aggregate_metrics
from .report import write_reports
from app.main import app


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run evaluation for mcp-material")
    parser.add_argument("--output", default="eval/out", help="Output directory for reports")
    args = parser.parse_args(argv)

    out_dir = Path(args.output)
    cases = load_dataset()
    client = TestClient(app)
    raw_results = run_cases(cases, client)

    case_results: List[Dict] = []
    for case, res in zip(cases, raw_results):
        metrics = compute_case_metrics(case, res["priced_bom"])
        case_results.append({"case_id": case.id, "metrics": metrics, "priced_bom": res["priced_bom"]})

    aggregate = aggregate_metrics([r["metrics"] for r in case_results])
    write_reports(case_results, aggregate, out_dir)


if __name__ == "__main__":
    main()
