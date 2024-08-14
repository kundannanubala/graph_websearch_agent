from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from termcolor import colored
from agents.agents import (
    PlannerAgent,
    SummarizationAgent,
    ReviewerAgent,
    RouterAgent,
    ReportGenerationAgent
)
from prompts.prompts import (
    planner_prompt_template,
    summarization_prompt_template,
    reviewer_prompt_template,
    router_prompt_template,
    report_generation_prompt_template,
    planner_guided_json,
    summarization_guided_json,
    reviewer_guided_json,
    router_guided_json,
    report_generation_guided_json
)
from tools.xml_parser_tool import xml_parser_tool
from tools.content_scraper_tool import content_scraper_tool
from tools.keyword_filter_tool import keyword_filter_tool  # Import the new tool
from tools.local_article_loader_tool import local_article_loader_tool #New tool
from tools.review_filter_tool import review_filter_tool #new review filter tool which removes the articles which failed the review
import json
from langchain_core.messages import HumanMessage

class OutputNode:
    def process(self, final_report):
        final_report_value = final_report() if callable(final_report) else final_report

        # Handle the case where final_report_value is None
        if final_report_value is None:
            error_message = "Error: Final report is None. No content to process."
            print(error_message)
            with open("D:/VentureInternship/final_report.txt", "w") as file:
                file.write(error_message)
            return error_message

        # Extract content from HumanMessage object or use the value directly
        if isinstance(final_report_value, HumanMessage):
            report_content = final_report_value.content
        else:
            report_content = final_report_value

        # Try to parse the content as JSON
        try:
            if isinstance(report_content, str):
                report_data = json.loads(report_content)
            elif isinstance(report_content, dict):
                report_data = report_content
            else:
                raise ValueError(f"Unexpected report content type: {type(report_content)}")
        except json.JSONDecodeError:
            error_message = f"Failed to parse final_report content as JSON: {report_content}"
            print(error_message)
            with open("D:/VentureInternship/final_report.txt", "w") as file:
                file.write(error_message)
            return error_message

        # Process the report content
        human_readable_report = self.generate_human_readable_report(report_data)

        # Write the human-readable report to a file
        with open("D:/VentureInternship/final_report.txt", "w") as file:
            file.write(human_readable_report)

    def generate_human_readable_report(self, report_data):
        human_readable_report = "Final Report\n\n"

        if 'reports' in report_data and isinstance(report_data['reports'], list):
            for index, report in enumerate(report_data['reports'], 1):
                human_readable_report += f"Report {index}:\n"
                human_readable_report += f"Introduction: {report.get('introduction', 'N/A')}\n\n"

                article = report.get('article', {})
                human_readable_report += f"Article: {article.get('title', 'N/A')}\n"
                human_readable_report += f"matching_keywords: {article.get('matching_keywords','N/A')}\n"
                human_readable_report += f"Author: {article.get('author', 'N/A')}\n"
                human_readable_report += f"Published Date: {article.get('published_date', 'N/A')}\n"
                human_readable_report += f"Summary: {article.get('summary', 'N/A')}\n"
                human_readable_report += f"Link: {article.get('link', 'N/A')}\n"
                if 'image_url' in article:
                    human_readable_report += f"Image URL: {article['image_url']}\n"

                human_readable_report += f"\nConclusion: {report.get('conclusion', 'N/A')}\n\n"
                human_readable_report += "-" * 50 + "\n\n"
        else:
            human_readable_report += "No reports found in the final report content."

        return human_readable_report

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

    # graph.add_node(
    #     "xml_parser",
    #     lambda state: xml_parser_tool(
    #         rss_feed_urls=get_agent_graph_state(state=state, state_key="rss_urls"),
    #         state=state
    #     )
    # )

    # graph.add_node(
    #     "content_scraper",
    #     lambda state: content_scraper_tool(
    #         state=state
    #     )
    # )
    # Replace xml_parser and content_scraper with local_article_loader
    graph.add_node(
        "local_article_loader",
        lambda state: local_article_loader_tool(state)
    )

    graph.add_node(
        "keyword_filter",
        lambda state: keyword_filter_tool(state)
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
            filtered_articles=lambda: get_agent_graph_state(state=state, state_key="keyword_filter_response"),
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
    "review_filter",
    lambda state: review_filter_tool(state) 
    ) #new node added before sending to report generator to reduce unnecessary context

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
            articles=lambda: get_agent_graph_state(state=state, state_key="keyword_filter_response"),
            summaries=lambda: get_agent_graph_state(state=state, state_key="summarization_latest"),
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            prompt=report_generation_prompt_template
        )
    )

    graph.add_node(
        "output",
        lambda state: OutputNode().process(get_agent_graph_state(state=state, state_key="report_generation_response_latest"))
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
            next_agent = "review_filter"

        return next_agent

    # Add edges to the graph
    graph.set_entry_point("planner")
    graph.set_finish_point("output")
    graph.add_edge("planner", "local_article_loader") #updated graph edges with local article loader
    graph.add_edge("local_article_loader", "keyword_filter")
    graph.add_edge("keyword_filter", "summarization")
    graph.add_edge("summarization", "reviewer")
    graph.add_edge("reviewer", "router")
    graph.add_conditional_edges(
        "router",
        lambda state: pass_review(state=state),
    )
    graph.add_edge("review_filter", "report_generator")
    graph.add_edge("report_generator", "output")
    return graph

def compile_workflow(graph):
    workflow = graph.compile()
    return workflow