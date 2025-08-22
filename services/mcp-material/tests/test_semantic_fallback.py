from app.services.catalog import MaterialCatalog


def test_semantic_fallback(monkeypatch):
    monkeypatch.setattr('app.services.catalog.HAS_EMB', False)
    cat = MaterialCatalog()
    # should load without embeddings and not crash
    cat.load()
    assert cat.match("бетон") == []
