# import json
# import yaml
# import os
from termcolor import colored
from models.openai_models import get_open_ai, get_open_ai_json
from models.ollama_models import OllamaModel, OllamaJSONModel
from models.vllm_models import VllmJSONModel, VllmModel
from models.groq_models import GroqModel, GroqJSONModel
from models.claude_models import ClaudModel, ClaudJSONModel
from models.gemini_models import GeminiModel, GeminiJSONModel
from langchain_core.messages import HumanMessage
import json
from prompts.prompts import (
    planner_prompt_template,
    summarization_prompt_template,
    reviewer_prompt_template,
    router_prompt_template,
    keyword_filter_prompt_template,
    report_generation_prompt_template
)
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState

class Agent:
    def __init__(self, state: AgentGraphState, model=None, server=None, temperature=0, model_endpoint=None, stop=None, guided_json=None):
        self.state = state
        self.model = model
        self.server = server
        self.temperature = temperature
        self.model_endpoint = model_endpoint
        self.stop = stop
        self.guided_json = guided_json

    def get_llm(self, json_model=True):
        if self.server == 'openai':
            return get_open_ai_json(model=self.model, temperature=self.temperature) if json_model else get_open_ai(model=self.model, temperature=self.temperature)
        if self.server == 'ollama':
            return OllamaJSONModel(model=self.model, temperature=self.temperature) if json_model else OllamaModel(model=self.model, temperature=self.temperature)
        if self.server == 'vllm':
            return VllmJSONModel(
                model=self.model, 
                guided_json=self.guided_json,
                stop=self.stop,
                model_endpoint=self.model_endpoint,
                temperature=self.temperature
            ) if json_model else VllmModel(
                model=self.model,
                model_endpoint=self.model_endpoint,
                stop=self.stop,
                temperature=self.temperature
            )
        if self.server == 'groq':
            return GroqJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else GroqModel(
                model=self.model,
                temperature=self.temperature
            )
        if self.server == 'claude':
            return ClaudJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else ClaudModel(
                model=self.model,
                temperature=self.temperature
            )
        if self.server == 'gemini':
            return GeminiJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else GeminiModel(
                model=self.model,
                temperature=self.temperature
            )      

    def update_state(self, key, value):
        self.state = {**self.state, key: value}

class PlannerAgent(Agent):
    def invoke(self, feedback=None, prompt=planner_prompt_template):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        planner_prompt = prompt.format(
            feedback=feedback_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": planner_prompt},
            {"role": "user", "content": "Begin planning the RSS feed processing tasks."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("planner_response", response)
        with open("D:/VentureInternship/response.txt", "w") as file:
            file.write(f"Planner: {response}")

        return self.state
    

class KeywordFilterAgent(Agent):
    def invoke(self, articles, keywords, prompt=keyword_filter_prompt_template):
        articles_value = articles() if callable(articles) else articles
        keywords_value = keywords() if callable(keywords) else keywords

        # Extract content from HumanMessage objects
        articles_content = []
        for article in articles_value:
            if isinstance(article, HumanMessage):
                article_data = json.loads(article.content)
                articles_content.extend(article_data['articles'])

        # Convert articles to a string format for the prompt
        articles_str = " ".join([f"Title: {article['title']} Summary: {article['summary']}" for article in articles_content])

        keyword_filter_prompt = prompt.format(
            articles=articles_str,
            keywords=keywords_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": keyword_filter_prompt},
            {"role": "user", "content": "Filter the articles based on the specified keywords."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("keyword_filter_response", response)
        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Keyword Filter: {response}")
        return self.state

class SummarizationAgent(Agent):
    def invoke(self, filtered_articles, feedback=None, prompt=summarization_prompt_template):
      
        feedback_value = feedback() if callable(feedback) else feedback
        filtered_articles_value = filtered_articles() if callable(filtered_articles) else filtered_articles
        feedback_value = check_for_content(feedback_value)

        # Extract content from HumanMessage objects
        articles_content = []
        for article in filtered_articles_value:
            if isinstance(article, HumanMessage):
                article_data = json.loads(article.content)
                articles_content.extend(article_data['articles'])

        # Convert articles to a string format for the prompt
        articles_str = " ".join([f"Title: {article['title']} Summary: {article['summary']}" for article in articles_content])

        summarization_prompt = prompt.format(
            filtered_articles=articles_str,
            feedback=feedback_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": summarization_prompt},
            {"role": "user", "content": "Summarize the filtered RSS feed articles."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("summarization_response", response)
        
        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Summarizer: {response}\n")
        return self.state


class ReviewerAgent(Agent):
    def invoke(self, summaries, prompt=reviewer_prompt_template, feedback=None,keywords=None):
        feedback_value = feedback() if callable(feedback) else feedback
        summaries_value = summaries() if callable(summaries) else summaries
        feedback_value = check_for_content(feedback_value)

        reviewer_prompt = prompt.format(
            summaries=summaries_value,
            keywords=keywords,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
            state=self.state
        )

        messages = [
            {"role": "system", "content": reviewer_prompt},
            {"role": "user", "content": "Review the summarized articles for accuracy and relevance."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("reviewer_response", response)
        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Reviewer: {response}\n")
        return self.state


class RouterAgent(Agent):
    def invoke(self, feedback,prompt=router_prompt_template):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        router_prompt = prompt.format(
            feedback=feedback_value
        )

        messages = [
            {"role": "system", "content": router_prompt},
            {"role": "user", "content": f"Route the conversation based on the reviewer's feedback."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("router_response", response)
        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Router: {response}\n")
        return self.state

class ReportGenerationAgent(Agent):
    def invoke(self, summaries, feedback=None, prompt=report_generation_prompt_template):
        feedback_value = feedback() if callable(feedback) else feedback
        summaries_value = summaries() if callable(summaries) else summaries
        feedback_value = check_for_content(feedback_value)

        report_generation_prompt = prompt.format(
            summaries=summaries_value,
            feedback=feedback_value,
            datetime=get_current_utc_datetime()
        )

        messages = [
            {"role": "system", "content": report_generation_prompt},
            {"role": "user", "content": "Generate the comprehensive report based on the summarized articles."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        self.update_state("final_report", response)
        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Report Generator: {response}\n")
        return self.state

