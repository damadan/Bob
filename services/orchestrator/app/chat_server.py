from fastapi import FastAPI
from pydantic import BaseModel
from .agent import build_agent

app = FastAPI(title="AEC Agent")
agent = None

class ChatRequest(BaseModel):
    message: str

@app.on_event("startup")
def _startup():
    global agent
    try:
        agent = build_agent()
    except Exception as e:
        # if no key, agent remains None; expose health but return 503 on chat
        agent = None

@app.get("/health")
def health():
    return {"status":"ok","agent_ready": bool(agent)}

@app.post("/chat")
def chat(req: ChatRequest):
    if not agent:
        return {"error":"Agent is not ready. Set OPENAI_API_KEY or configure local provider."}
    reply = agent.run(req.message)
    return {"reply": reply}
