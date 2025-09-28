import json
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from .config import get_llm
from .tools import add_user_tool, create_ticket_tool, view_ticket_tool, update_status_tool, list_tickets_tool, reset_database_tool, delete_user_tool, delete_ticket_tool, show_users_tool
from .nlp_prompts import ROUTER_SYSTEM_PROMPT


def _router_call(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()
    messages = state.get("messages", []) 
    sys_prompt = SystemMessage(content=ROUTER_SYSTEM_PROMPT)
    input_messages = [sys_prompt] + [
        HumanMessage(m["content"]) if m["role"]=="user" else AIMessage(m["content"]) for m in messages
    ]
    # LLM will output a JSON object describing intent/args or unsupported text
    router_query = input_messages + [HumanMessage("Return ONLY a JSON object for the latest user message.")]
    res = llm.invoke(router_query)
    text = res.content.strip()
    try:
        data = json.loads(text)
    except Exception:
        # unsupported
        data = {"intent":"unsupported","message":"I can't help with that."}
    return {"router": data}

def _tool_exec(tool, mapping):
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        args = state["router"].get("args", {})
        tool_args = {key: args.get(key) for key in mapping.keys()}
        try:
            if tool_args:
                out = tool.invoke(tool_args)          # tools with params
            else:
                out = tool.func()    
        except Exception as e:
            out = f"Error: {e}"
        prior = state.get("messages", [])
        return {"messages": prior + [{"role": "assistant", "content": out}]}
    return run

def build_app():
    sg = StateGraph(dict)  # {"messages": [.....], "router": {.....}}
    memory = MemorySaver()

    # Nodes
    sg.add_node("route", RunnableLambda(_router_call))
    sg.add_node("add_user", RunnableLambda(_tool_exec(add_user_tool, {"user_id":None, "name":None})))
    sg.add_node("create_ticket", RunnableLambda(_tool_exec(create_ticket_tool, {"title":None,"assignee_name":None})))
    sg.add_node("view_ticket", RunnableLambda(_tool_exec(view_ticket_tool, {"user_id": None})))
    sg.add_node("update_status", RunnableLambda(_tool_exec(update_status_tool, {"user_id": None, "status": None})))
    sg.add_node("list_tickets", RunnableLambda(_tool_exec(list_tickets_tool, {"kind":None})))
    sg.add_node("show_users", RunnableLambda(_tool_exec(show_users_tool, {})))
    sg.add_node("delete_user", RunnableLambda(_tool_exec(delete_user_tool, {"user_id": None})))
    sg.add_node("delete_ticket", RunnableLambda(_tool_exec(delete_ticket_tool, {"user_id": None})))
    sg.add_node("reset_database", RunnableLambda(_tool_exec(reset_database_tool, {})))
    sg.add_node("unsupported", RunnableLambda(lambda s: {"messages": s.get("messages", []) + [{"role":"assistant","content": s.get("router", {}).get("message","I can't help with that.")}]}))
    sg.add_node("clarify", RunnableLambda(lambda s: {"messages": s.get("messages", []) + [{"role":"assistant","content": s.get("router", {}).get("message","Could you provide the missing details?")}]}))

    # Edges
    sg.add_edge(START, "route")

    def decide(state: Dict[str, Any]) -> str:
        intent = state["router"].get("intent")
        return {
            "add_user":"add_user",
            "create_ticket":"create_ticket",
            "view_ticket":"view_ticket",
            "update_status":"update_status",
            "list_tickets":"list_tickets",
            "show_users": "show_users",
            "reset_database":"reset_database",
            "delete_user":"delete_user",       
            "delete_ticket":"delete_ticket",
            "unsupported":"unsupported",
            "clarify":"clarify",
        }.get(intent, "unsupported")

    # Route from Router to the appropriate node
    sg.add_conditional_edges("route", decide, {
        "add_user": "add_user",
        "create_ticket": "create_ticket",
        "view_ticket": "view_ticket",
        "update_status": "update_status",
        "list_tickets": "list_tickets",
        "show_users": "show_users",
        "delete_user": "delete_user",
        "delete_ticket": "delete_ticket",
        "reset_database": "reset_database",
        "unsupported": "unsupported",
        "clarify": "clarify",
    })

    # Terminate nodes
    for node in ["add_user", "create_ticket", "view_ticket", "update_status", "list_tickets", "delete_user", "delete_ticket", "show_users", "reset_database", "unsupported", "clarify"]:
        sg.add_edge(node, END)

    app = sg.compile()
    return app
