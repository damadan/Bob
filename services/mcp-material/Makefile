.PHONY: run dev test lint format docker-up docker-build

run:
	PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8080

dev:
	ENV=dev PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

test:
	PYTHONPATH=. pytest -q

docker-build:
	docker build -t mcp-material:dev .

docker-up:
	docker compose up --build
