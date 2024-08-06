import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from termcolor import colored
from agents.agents import (
    PlannerAgent,
    SummarizationAgent,
    ReviewerAgent,
    RouterAgent,
    KeywordFilterAgent,
    ReportGenerationAgent
)
from prompts.prompts import (
    planner_prompt_template,
    summarization_prompt_template,
    reviewer_prompt_template,
    router_prompt_template,
    keyword_filter_prompt_template,
    report_generation_prompt_template,
    planner_guided_json,
    summarization_guided_json,
    reviewer_guided_json,
    router_guided_json,
    keyword_filter_guided_json,
    report_generation_guided_json
)
from tools.xml_parser_tool import xml_parser_tool  # Import the xml_parser_tool
from tools.content_scraper_tool import content_scraper_tool  # Import the content_scraper_tool

class OutputNode:
    def process(self, final_report):
        final_report_value = final_report() if callable(final_report) else final_report
        
        # Display or handle the final report as needed
        with open("D:/VentureInternship/final_report.txt", "w") as file:
            file.write(f"Final Report: {final_report_value}")

        
        # Assuming the final report needs to be returned or saved, we can return it here
        return final_report_value

from states.state import AgentGraphState, get_agent_graph_state, state

def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    graph.add_node(
        "planner", 
        lambda state: PlannerAgent(
            state=state,
            model=model,
            server=server,
            guided_json=planner_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=planner_prompt_template
        )
    )

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
        "keyword_filter",
        lambda state: KeywordFilterAgent(
            state=state,
            model=model,
            server=server,
            guided_json=keyword_filter_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            articles=lambda: get_agent_graph_state(state=state, state_key="content_scraper_response"),
            keywords=lambda: get_agent_graph_state(state=state, state_key="keywords"),
            prompt=keyword_filter_prompt_template
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
            filtered_articles=lambda: get_agent_graph_state(state=state, state_key="keyword_filter_latest"),
            keywords=lambda: get_agent_graph_state(state=state, state_key="keywords"),
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=summarization_prompt_template
        )
    )

    graph.add_node(
        "reviewer", 
        lambda state: ReviewerAgent(
            state=state,
            model=model,
            server=server,
            guided_json=reviewer_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            summaries=lambda: get_agent_graph_state(state=state, state_key="summarization_latest"),
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
            prompt=reviewer_prompt_template,
            keywords=lambda: get_agent_graph_state(state=state, state_key="keywords")
        )
    )

    graph.add_node(
        "router", 
        lambda state: RouterAgent(
            state=state,
            model=model,
            server=server,
            guided_json=router_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
            prompt=router_prompt_template
        )
    )

    graph.add_node(
        "report_generator",
        lambda state: ReportGenerationAgent(
            state=state,
            model=model,
            server=server,
            guided_json=report_generation_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            summaries=lambda: get_agent_graph_state(state=state, state_key="summarization_latest"),
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=report_generation_prompt_template
        )
    )

    graph.add_node(
        "output",
        lambda state: OutputNode().process(get_agent_graph_state(state=state, state_key="final_report"))
    )

    # Define the edges in the agent graph
    def pass_review(state: AgentGraphState):
        review_list = state["router_response"]
        if review_list:
            review = review_list[-1]
        else:
            review = "No review"

        if review != "No review":
            if isinstance(review, HumanMessage):
                review_content = review.content
            else:
                review_content = review
            
            review_data = json.loads(review_content)
            next_agent = review_data["next_agent"]
        else:
            next_agent = "report_generator"

        return next_agent

    # Add edges to the graph
    graph.set_entry_point("planner")
    graph.set_finish_point("output")
    graph.add_edge("planner", "xml_parser")
    graph.add_edge("xml_parser", "content_scraper")
    graph.add_edge("content_scraper", "keyword_filter")
    graph.add_edge("keyword_filter", "summarization")
    graph.add_edge("summarization", "reviewer")
    graph.add_edge("reviewer", "router")
    graph.add_conditional_edges(
        "router",
        lambda state: pass_review(state=state),
    )

    graph.add_edge("report_generator", "output")

    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow
