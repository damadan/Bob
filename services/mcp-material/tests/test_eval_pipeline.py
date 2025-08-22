from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from eval.dataset import load_dataset
from eval import runner, metrics, report


def test_eval_pipeline(tmp_path, monkeypatch):
    cases = load_dataset()
    case = cases[0]

    def fake_run_case(client, case):
        return {
            "case_id": case.id,
            "priced_bom": {
                "items": [
                    {
                        "name": "Бетон C25/30",
                        "unit": "m3",
                        "qty": 12.5,
                        "unit_price": 95.4,
                        "currency": "EUR",
                    }
                ],
                "subtotal": 100.0,
                "currency": "EUR",
                "gaps": [],
            },
        }

    monkeypatch.setattr(runner, "run_case", fake_run_case)

    client = TestClient(app)
    results = runner.run_cases([case], client)
    case_metrics = [metrics.compute_case_metrics(case, r["priced_bom"]) for r in results]
    agg = metrics.aggregate_metrics(case_metrics)

    out_dir = tmp_path / "out"
    report.write_reports(
        [{"case_id": case.id, "metrics": case_metrics[0]}], agg, out_dir
    )

    assert "coverage" in case_metrics[0]
    assert "precision_at_1" in case_metrics[0]
    assert (out_dir / "results.json").exists()
    assert (out_dir / "report.md").exists()
