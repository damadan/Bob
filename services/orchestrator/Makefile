.PHONY: dev agent
dev:
	uvicorn app.server:app --host 0.0.0.0 --port 8090 --reload
agent:
	uvicorn app.chat_server:app --host 0.0.0.0 --port 8091 --reload
