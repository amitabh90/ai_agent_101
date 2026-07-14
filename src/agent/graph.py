from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import (
    prompt_user_node,
    fetch_changes_node,
    analyze_code_node,
    display_results_node,
    request_approval_node,
    create_pr_node,
    save_state_node,
    handle_error_node
)


def should_continue_after_fetch(state: AgentState) -> str:
    if state.get("error"):
        return "handle_error"
    if not state.get("commits") or len(state["commits"]) == 0:
        return "save_state"
    return "analyze_code"


def should_continue_after_approval(state: AgentState) -> str:
    if state.get("error"):
        return "handle_error"
    if state.get("approval_status") == "approved":
        return "create_pr"
    return "save_state"


def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("prompt_user", prompt_user_node)
    workflow.add_node("fetch_changes", fetch_changes_node)
    workflow.add_node("analyze_code", analyze_code_node)
    workflow.add_node("display_results", display_results_node)
    workflow.add_node("request_approval", request_approval_node)
    workflow.add_node("create_pr", create_pr_node)
    workflow.add_node("save_state", save_state_node)
    workflow.add_node("handle_error", handle_error_node)
    
    workflow.set_entry_point("prompt_user")
    
    workflow.add_edge("prompt_user", "fetch_changes")
    
    workflow.add_conditional_edges(
        "fetch_changes",
        should_continue_after_fetch,
        {
            "analyze_code": "analyze_code",
            "save_state": "save_state",
            "handle_error": "handle_error"
        }
    )
    
    workflow.add_edge("analyze_code", "display_results")
    workflow.add_edge("display_results", "request_approval")
    
    workflow.add_conditional_edges(
        "request_approval",
        should_continue_after_approval,
        {
            "create_pr": "create_pr",
            "save_state": "save_state",
            "handle_error": "handle_error"
        }
    )
    
    workflow.add_edge("create_pr", "save_state")
    workflow.add_edge("save_state", END)
    workflow.add_edge("handle_error", END)
    
    return workflow.compile()


agent_graph = create_agent_graph()
