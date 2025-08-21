.PHONY: run dev test lint format docker-up docker-build

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080

dev:
	ENV=dev uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

test:
	pytest -q

docker-build:
	docker build -t mcp-material:dev .

docker-up:
	docker compose up --build
