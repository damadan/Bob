#!/bin/bash
set -e
pip install -r requirements-core.txt -r requirements-extras.txt >/dev/null
pytest -q
uvicorn app.main:app --port 8090 --host 127.0.0.1 &
PID=$!
sleep 1
curl -fsS http://127.0.0.1:8090/health >/dev/null
curl -fsS http://127.0.0.1:8090/metrics >/dev/null
curl -fsS http://127.0.0.1:8090/docs >/dev/null
kill $PID
echo "SANITY PASS"
