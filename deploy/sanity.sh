#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
docker compose --env-file ./.env.prod -f docker-compose.prod.yml up -d --build
sleep 5
echo "Check nginx → orchestrator"
curl -sf "http://localhost:${WEB_PORT}/" >/dev/null
echo "Check mcp-material health"
curl -sf "http://localhost:${WEB_PORT}/mcp/material/health" || curl -sf "http://localhost:${WEB_PORT}/mcp/material/../health" || true
echo "Check prometheus"
curl -sf "http://localhost:${PROMETHEUS_PORT}" >/dev/null
echo "OK"
