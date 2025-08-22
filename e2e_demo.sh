#!/usr/bin/env bash
set -e

echo "[1/3] Ensure MCP Material is running separately (services/mcp-material -> make dev)"
echo "[2/3] Starting Orchestrator on :8090"
cd services/orchestrator
pip install -r requirements.txt >/dev/null
make dev
