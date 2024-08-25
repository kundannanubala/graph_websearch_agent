from typing import TypedDict, Annotated, Dict, Any
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    user_input: str
    knowledge_base: Annotated[list, add_messages]
    preprocessed_data: Dict[str, Any]
    analysis_node1_response: Annotated[list, add_messages]
    analysis_node2_response: Annotated[list, add_messages]
    feedback_response: Annotated[list, add_messages]
    scoring_response: Annotated[list, add_messages]
    paraphrased_response: Annotated[list, add_messages]
    formatted_report: Annotated[list, add_messages]

# Define the function to get agent graph state
def get_agent_graph_state(state: AgentGraphState, state_key: str):
    if state_key == "user_input":
        return state["user_input"]
    
    elif state_key == "knowledge_base":
        return state["knowledge_base"]

    elif state_key == "preprocessed_data":
        return state["preprocessed_data"]

    elif state_key == "analysis_node1_all":
        return state["analysis_node1_response"]
    elif state_key == "analysis_node1_latest":
        if state["analysis_node1_response"]:
            return state["analysis_node1_response"][-1]
        else:
            return state["analysis_node1_response"]

    elif state_key == "analysis_node2_all":
        return state["analysis_node2_response"]
    elif state_key == "analysis_node2_latest":
        if state["analysis_node2_response"]:
            return state["analysis_node2_response"][-1]
        else:
            return state["analysis_node2_response"]

    elif state_key == "feedback_all":
        return state["feedback_response"]
    elif state_key == "feedback_latest":
        if state["feedback_response"]:
            return state["feedback_response"][-1]
        else:
            return state["feedback_response"]

    elif state_key == "scoring_all":
        return state["scoring_response"]
    elif state_key == "scoring_latest":
        if state["scoring_response"]:
            return state["scoring_response"][-1]
        else:
            return state["scoring_response"]

    elif state_key == "paraphrased_all":
        return state["paraphrased_response"]
    elif state_key == "paraphrased_latest":
        if state["paraphrased_response"]:
            return state["paraphrased_response"][-1]
        else:
            return state["paraphrased_response"]

    elif state_key == "formatted_report_all":
        return state["formatted_report"]
    elif state_key == "formatted_report_latest":
        if state["formatted_report"]:
            return state["formatted_report"][-1]
        else:
            return state["formatted_report"]

    else:
        return None

# Initialize the state
state = {
    "knowledge_base":[],
    "user_input": "",
    "preprocessed_data": {},
    "analysis_node1_response": [],
    "analysis_node2_response": [],
    "feedback_response": [],
    "scoring_response": [],
    "paraphrased_response": [],
    "formatted_report": [],
}
