from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentGraphState(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]

def get_agent_graph_state(state: AgentGraphState, state_key: str):
    if state_key == "user_input":
        return state["user_input"]

    elif state_key.endswith("_all"):
        agent_name = state_key[:-4]  # Remove '_all' from the end
        return [msg for msg in state["messages"] if msg.role == agent_name]

    elif state_key.endswith("_latest"):
        agent_name = state_key[:-7]  # Remove '_latest' from the end
        messages = [msg for msg in state["messages"] if msg.role == agent_name]
        return messages[-1] if messages else None

    else:
        return None

# Initialize the state
state = {
    "user_input": "",
    "messages": [],
}