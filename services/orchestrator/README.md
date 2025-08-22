# orchestrator

Coordinator service that sequences requests to downstream microservices.

## Step 10: UX & E2E Demo

The service exposes a small web UI and JSON API that run the full material
pipeline (parse → extract → price → substitutions → export).

### Quick start

```bash
cd services/orchestrator
pip install -r requirements.txt
make dev    # http://localhost:8090/
```

Open `http://localhost:8090/` in a browser to upload a PDF/IFC. On success it
returns links to JSON/XLSX/PDF artifacts and a priced preview table. Artifact
links are served by MCP at `${MCP_BASE_URL}/mcp/material/download/...`.

### curl examples

```bash
curl -s -X POST http://localhost:8090/run \
  -H "Content-Type: application/json" \
  -d '{"project_id":"demo","file_uri":"resource://project/demo/files/spec.pdf","region":"EU-Central"}'
```

```bash
curl -s -X POST http://localhost:8090/run_multipart \
  -F "project_id=demo" \
  -F "region=EU-Central" \
  -F "file=@/path/to/drawing.pdf"
```

### LLM Agent (Step 9)
- Set `OPENAI_API_KEY` in env (do NOT commit keys).
- Run HTTP agent server:
  ```
  export OPENAI_API_KEY=***
  cd services/orchestrator
  pip install -r requirements.txt
  make agent   # http://localhost:8091
  curl -s -X POST http://localhost:8091/chat -H "Content-Type: application/json" -d '{"message":"Сделай смету из resource://project/demo/files/spec.pdf и отдай PDF/Excel"}'
  ```
- Local fallback: set `LLM_PROVIDER=local` and `LOCAL_LLM_BASE_URL=http://localhost:8000/v1`.
