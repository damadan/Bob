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
