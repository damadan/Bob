# orchestrator

Coordinator service that sequences requests to downstream microservices.

## Endpoints
- `POST /run`
- `POST /run_multipart`
- `POST /chat`

Runs on **8090**.

### curl examples

```bash
curl -X POST "http://localhost:8090/run" -H "Content-Type: application/json" -d '{"steps":[]}'
```

```bash
curl -X POST "http://localhost:8090/run_multipart" -F "file=@./sample.txt"
```

- **LLM Agent (Step 9)**:
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
