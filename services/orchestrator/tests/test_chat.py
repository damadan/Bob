
def test_chat(client):
    message = "hi"
    r = client.post("/chat", json={"message": message})
    assert r.status_code == 200
    assert r.json()["reply"] == f"Echo: {message}"

