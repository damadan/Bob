# Sanity checklist

## mcp-material
```bash
cd services/mcp-material
pip install -r requirements-core.txt
pip install -r requirements-extras.txt
pytest -q
make dev  # starts server on http://0.0.0.0:8080
```
