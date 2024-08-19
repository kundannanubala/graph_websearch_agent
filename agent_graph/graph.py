import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from termcolor import colored
from agents.agents import (
    SummarizationAgent
)
from prompts.prompts import (
    summarization_prompt_template,
    summarization_guided_json,
)
from tools.xml_parser_tool import xml_parser_tool  # Import the xml_parser_tool
from tools.content_scraper_tool import content_scraper_tool  # Import the content_scraper_tool
from tools.keyword_filter_tool import keyword_filter_tool #Import the keyword_filter_tool

import json
from langchain_core.messages import HumanMessage


from states.state import AgentGraphState, get_agent_graph_state, state

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    graph.add_node(
        "xml_parser",
        lambda state: xml_parser_tool(
            rss_feed_urls=get_agent_graph_state(state=state, state_key="rss_urls"),
            state=state
        )
    )

    graph.add_node(
        "content_scraper",
        lambda state: content_scraper_tool(
            state=state
        )
    )

    graph.add_node(
        "summarization",
        lambda state: SummarizationAgent(
            state=state,
            model=model,
            server=server,
            guided_json=summarization_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            articles=lambda: get_agent_graph_state(state=state, state_key="content_scraper_response"),
            keywords=lambda: get_agent_graph_state(state=state, state_key="keywords"),
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=summarization_prompt_template
        )
    )
    
    graph.add_node(
        "keyword_filter",
        lambda state: keyword_filter_tool(state)
    )

    graph.set_entry_point("xml_parser") # Making feed parsing as entry point
    graph.set_finish_point("keyword_filter")
    graph.add_edge("xml_parser", "content_scraper")
    graph.add_edge("content_scraper","summarization")
    graph.add_edge("summarization","keyword_filter")

    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow
