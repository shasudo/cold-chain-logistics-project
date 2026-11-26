"""DeepSeek ReAct agent built with LangChain's create_agent (the create_react_agent successor)."""

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver

import config
from src.tools import TOOLS

_agent = None


def get_agent():
    """Build the agent once; raises a clear error when the DeepSeek key is missing."""
    global _agent
    if _agent is None:
        if not config.DEEPSEEK_API_KEY:
            raise RuntimeError(
                "Missing DEEPSEEK_API_KEY in .env — copy .env.example to .env and fill it in."
            )
        model = ChatDeepSeek(
            model=config.DEEPSEEK_MODEL,
            api_key=config.DEEPSEEK_API_KEY,
            temperature=0,
        )
        _agent = create_agent(
            model=model,
            tools=TOOLS,
            system_prompt=config.SYSTEM_PROMPT_PATH.read_text(),
            checkpointer=InMemorySaver(),
        )
    return _agent


def ask(question: str, thread_id: str) -> tuple[str, list[dict]]:
    """Ask the agent something. Returns (final_answer, trace of tool calls).

    Conversation memory lives in the checkpointer under `thread_id`,
    so callers never pass history around.
    """
    agent = get_agent()
    trace: list[dict] = []
    pending: dict[str, dict] = {}
    answer = ""
    events = agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="updates",
    )
    for event in events:
        for payload in event.values():
            for msg in payload.get("messages", []):
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    for call in msg.tool_calls:
                        step = {"tool": call["name"], "args": call["args"], "output": ""}
                        trace.append(step)
                        pending[call["id"]] = step
                elif isinstance(msg, ToolMessage):
                    if msg.tool_call_id in pending:
                        pending[msg.tool_call_id]["output"] = msg.content
                elif isinstance(msg, AIMessage) and msg.content:
                    answer = msg.content
    return (answer or "(empty response)", trace)


if __name__ == "__main__":
    print(f"DeepSeek agent ({config.DEEPSEEK_MODEL}). Type 'exit' to quit.\n")
    while True:
        user_input = input("Dispatcher > ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        reply, _ = ask(user_input, thread_id="cli")
        print(f"\n{reply}\n")
