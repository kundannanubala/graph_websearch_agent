import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from termcolor import colored
from agents.agents import (
    AnalysisNode2Agent,
    FeedbackGenerationAgent,
    ScoringAgent,
    ParaphrasingAgent,
)
from tools.preprocessing_tool import preprocessing_tool
from tools.analysis_node1_tool import analysis_node1_tool
from tools.knowledge_base_loader import knowledge_base_loader
from tools.format_report import format_report
from states.state import AgentGraphState, get_agent_graph_state, state

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    # KowledgeBaseLoading Node
    graph.add_node(
        "knowledgeBase",
        lambda state: knowledge_base_loader(state)
    )
    # Preprocessing Node
    graph.add_node(
        "preprocessing",
        lambda state: preprocessing_tool(state)
    )

    # Analysis Node 1
    graph.add_node(
        "analysis_node1",
        lambda state: analysis_node1_tool(state)
    )

    # Analysis Node 2
    graph.add_node(
        "analysis_node2",
        lambda state: AnalysisNode2Agent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(state)
    )

    # Feedback Generation Node
    graph.add_node(
        "feedback_generation",
        lambda state: FeedbackGenerationAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(state)
    )

    # Scoring Node
    graph.add_node(
        "scoring",
        lambda state: ScoringAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(state)
    )

    # Paraphrasing Node
    graph.add_node(
        "paraphrasing",
        lambda state: ParaphrasingAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(state)
    )
    
    graph.add_node(
    "report_generation",
    lambda state: format_report()
    )


    # Set the entry point
    graph.set_entry_point("knowledgeBase")

    # Set the finish point
    graph.set_finish_point("report_generation")

    # Add edges to connect the nodes
    graph.add_edge("knowledgeBase", "preprocessing")
    graph.add_edge("preprocessing", "analysis_node1")
    graph.add_edge("analysis_node1", "analysis_node2")
    graph.add_edge("analysis_node2", "feedback_generation")
    graph.add_edge("feedback_generation", "scoring")
    graph.add_edge("scoring", "paraphrasing")
    graph.add_edge("paraphrasing", "report_generation")
    graph.set_finish_point("report_generation")

    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow