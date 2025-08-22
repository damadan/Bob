# Production Deploy (Step 11)

## Quick start
```bash
cd deploy
cp .env.prod .env.local && edit .env.local
docker compose --env-file .env.local -f docker-compose.prod.yml up -d --build
```

### Endpoints

- Web UI + Orchestrator: http://localhost:${WEB_PORT}/
- MCP Material (proxied): http://localhost:${WEB_PORT}/mcp/material/
- Prometheus: http://localhost:${PROMETHEUS_PORT}
- Grafana: http://localhost:${GRAFANA_PORT} (admin/admin)

### Notes

Nginx adds security headers, CORS, gzip, and rate limiting.

`/stub_status` is exposed for `nginx-prometheus-exporter`.

Set `MCP_API_KEY` to protect MCP; Orchestrator forwards it.

For TLS, replace nginx with Caddy or terminate TLS upstream (cloud LB).
