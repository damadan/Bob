
def test_run_multipart(client, tiny_pdf):
    r = client.post(
        "/run_multipart",
        params={"project_id": "xyz"},
        files={"file": ("dummy.pdf", tiny_pdf, "application/pdf")},
    )
    assert r.status_code == 200
    js = r.json()
    base = "http://localhost:8080"
    assert js["priced_bom"] == {}
    assert js["artifacts"]["excel_url"] == f"{base}/mcp/material/download/xyz/outputs/dummy.xlsx"
    assert js["artifacts"]["json_url"] == f"{base}/mcp/material/download/xyz/outputs/dummy.json"
    assert js["artifacts"]["pdf_url"] == f"{base}/mcp/material/download/xyz/outputs/dummy.pdf"

