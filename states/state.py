from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    rss_urls: list[str]
    keywords: list[str]
    xml_parser_response: Annotated[list, add_messages]
    content_scraper_response: Annotated[list, add_messages]
    keyword_filter_response: Annotated[list, add_messages]
    summarization_response: Annotated[list, add_messages]


# Define the function to get agent graph state
def get_agent_graph_state(state: AgentGraphState, state_key: str):
    if state_key == "rss_urls":
        return state["rss_urls"]
    
    if state_key == "keywords":
        return state["keywords"]

    elif state_key == "xml_parser_response":
        return state["xml_parser_response"]
    
    elif state_key == "content_scraper_response":
        return state["content_scraper_response"]

    elif state_key == "keyword_filter_all":
        return state["keyword_filter_response"]
    elif state_key == "keyword_filter_latest":
        if state["keyword_filter_response"]:
            return state["keyword_filter_response"][-1]
        else:
            return state["keyword_filter_response"]

    elif state_key == "summarization_all":
        return state["summarization_response"]
    elif state_key == "summarization_latest":
        if state["summarization_response"]:
            return state["summarization_response"][-1]
        else:
            return state["summarization_response"]

    else:
        return None

# Initialize the state
state = {
    "rss_urls": [],
    "keywords": [],
    "xml_parser_response": [],
    "content_scraper_response":[],
    "keyword_filter_response": [],
    "summarization_response": [],
}