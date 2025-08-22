
def test_run(client):
    payload = {"project_id": "123", "priced_bom": {"total": 1}}
    r = client.post("/run", json=payload)
    assert r.status_code == 200
    assert r.json()["priced_bom"]["total"] == 1

