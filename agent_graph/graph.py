from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agents.agents import (
    FlexibleAgent
)
from tools.preprocessing_tool import preprocessing_tool
from tools.analysis_node1_tool import analysis_node1_tool
from tools.knowledge_base_loader import knowledge_base_loader
from tools.format_report import format_report
from states.state import AgentGraphState
from prompts.prompts import (
    analysis_node2_prompt,
    feedback_generation_prompt,
    scoring_prompt,
    paraphrasing_prompt
)

plan = {
    "nodes": [
        {"name": "knowledgeBase", "type": "tool", "function": knowledge_base_loader},
        {"name": "preprocessing", "type": "tool", "function": preprocessing_tool},
        {"name": "analysis_node1", "type": "tool", "function": analysis_node1_tool},
        {"name": "analysis_node2", "type": "agent", "class": FlexibleAgent, 
         "prompt": analysis_node2_prompt, 
         "variables": ["preprocessing", "analysis_node1", "knowledgeBase"],
         "user_content": "Please provide your analysis."},
        {"name": "feedback_generation", "type": "agent", "class": FlexibleAgent,
         "prompt": feedback_generation_prompt,
         "variables": ["preprocessing", "analysis_node1", "analysis_node2", "knowledgeBase"],
         "user_content": "Please provide your detailed feedback."},
        {"name": "scoring", "type": "agent", "class": FlexibleAgent,
         "prompt": scoring_prompt,
         "variables": ["analysis_node1", "analysis_node2", "knowledgeBase"],
         "user_content": "Please provide the IELTS writing score breakdown."},
        {"name": "paraphrasing", "type": "agent", "class": FlexibleAgent,
         "prompt": paraphrasing_prompt,
         "variables": ["preprocessing", "scoring", "knowledgeBase"],
         "user_content": "Please provide the improved, Band 8 level paraphrased version."},
        {"name": "report_generation", "type": "tool", "function": format_report}
    ],
    "edges": [
        ("knowledgeBase", "preprocessing"),
        ("preprocessing", "analysis_node1"),
        ("analysis_node1", "analysis_node2"),
        ("analysis_node2", "feedback_generation"),
        ("feedback_generation", "scoring"),
        ("scoring", "paraphrasing"),
        ("paraphrasing", "report_generation")
    ],
    "entry_point": "knowledgeBase",
    "finish_point": "report_generation"
}

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    # Dynamically add nodes based on the plan
    for node in plan["nodes"]:
        if node["type"] == "tool":
            graph.add_node(node["name"], node["function"])
        elif node["type"] == "agent":
            graph.add_node(
                node["name"],
                lambda state, node=node: FlexibleAgent(
                    state=state,
                    role_name=node["name"],  # Pass the role name here
                    model=model,
                    server=server,
                    stop=stop,
                    model_endpoint=model_endpoint,
                    temperature=temperature
                ).invoke(state, node["prompt"], node["variables"], node["user_content"])
            )

    # Dynamically add edges based on the plan
    for edge in plan["edges"]:
        graph.add_edge(edge[0], edge[1])

    # Set entry and finish points
    graph.set_entry_point(plan["entry_point"])
    graph.set_finish_point(plan["finish_point"])

    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow