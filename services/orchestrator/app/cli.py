import argparse
from .state import PipelineState
from .graph import build_graph
from .config import settings


def main():
    p = argparse.ArgumentParser(description="AEC Orchestrator")
    p.add_argument("--project", required=True, help="project id")
    p.add_argument("--file-uri", required=True, help="resource://project/<id>/files/...")
    p.add_argument("--region", default=settings.MCP_REGION)
    args = p.parse_args()

    state = PipelineState(project_id=args.project, file_uri=args.file_uri, region=args.region)
    app = build_graph()
    final = app.invoke(state)
    print("--- DONE ---")
    print("JSON:", final.export_json_path)
    print("XLSX:", final.export_xlsx_path)
    print("PDF :", final.report_pdf_path)


if __name__ == "__main__":
    main()
