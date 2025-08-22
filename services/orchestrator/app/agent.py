from __future__ import annotations
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory
from .llm import build_llm
from .tools import parse_tool, extract_tool, price_tool, subs_tool, export_tool

SYSTEM_PROMPT = """Ты — AEC Copilot. Шаги:
1) parse_drawing(file_uri)
2) extract_bom(scope={'specs': ...} если parse вернул specs)
3) price_bom(bom, region)
4) suggest_substitutions(priced_bom) — опционально
5) export_results(project_id, priced_bom, filename_prefix='report')
Всегда возвращай пути к артефактам, если они получены."""

def build_agent():
    llm = build_llm()
    tools = [parse_tool, extract_tool, price_tool, subs_tool, export_tool]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=False,
        max_iterations=8,
        early_stopping_method="generate",
        memory=memory,
    )
    agent.agent_kwargs = agent.agent_kwargs or {}
    agent.agent_kwargs["extra_prompt_messages"] = [SystemMessage(content=SYSTEM_PROMPT), MessagesPlaceholder(variable_name="chat_history")]
    return agent
