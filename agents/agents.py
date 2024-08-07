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
    

from datetime import datetime
from langchain.schema import HumanMessage
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from prompts.prompts import keyword_filter_prompt_template

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
            elif isinstance(article, dict):
                articles_content.append(article)

        filtered_articles = []

        for article in articles_content:
            article_str = json.dumps(article)
            current_datetime = get_current_utc_datetime()
            keyword_filter_prompt = prompt.format(
                articles=article_str,
                keywords=keywords_value,
                datetime=current_datetime
            )
            
            # Define the response schema
            article_schema = ResponseSchema(name="article", description="A filtered article")
            response_schemas = [
                ResponseSchema(
                    name="filtered_articles",
                    description="List of filtered articles",
                    type="array",
                    items=article_schema
                )
            ]

            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
            format_instructions = output_parser.get_format_instructions()

            messages = [
                {"role": "system", "content": keyword_filter_prompt},
                {"role": "system", "content": f"Output Format: {format_instructions}"},
                {"role": "user", "content": "Filter the article based on the specified keywords."}
            ]

            llm = self.get_llm()
            ai_msg = llm.invoke(messages)
            response = ai_msg.content

            try:
                parsed_response = output_parser.parse(response)
                # Post-process to ensure data accuracy
                filtered_article = self.post_process_article(parsed_response['filtered_articles'], article, keywords_value)
                if filtered_article:
                    filtered_articles.append(filtered_article)
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                self.update_state("keyword_filter_error", error_msg)
                with open("D:/VentureInternship/error_log.txt", "a") as file:
                    file.write(f"\nError: {error_msg}")
                continue

        final_response = {"filtered_articles": filtered_articles}
        human_message = HumanMessage(role="system", content=json.dumps(final_response))
        self.update_state("keyword_filter_response", human_message)

        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"\nKeyword Filter: {json.dumps(final_response, indent=2)}")

        return self.state

    def post_process_article(self, filtered_articles, original_article, keywords):
        for filtered_article in filtered_articles:
            if filtered_article['title'].lower() == original_article['title'].lower():
                for keyword in keywords:
                    if keyword.lower() in original_article['title'].lower() or any(keyword.lower() in word.lower() for word in original_article['content'].split()):
                        return {
                            "title": original_article['title'],
                            "link": original_article['link'],
                            "author": original_article['author'],
                            "published_date": original_article['published_date'],
                            "content": original_article['content']
                        }
        return None
class SummarizationAgent(Agent):
    def invoke(self, filtered_articles, keywords, feedback=None, prompt=summarization_prompt_template):
        feedback_value = feedback() if callable(feedback) else feedback
        filtered_articles_value = filtered_articles() if callable(filtered_articles) else filtered_articles
        keywords_value = keywords() if callable(keywords) else keywords
        feedback_value = check_for_content(feedback_value)

        # Extract content from HumanMessage object
        articles_content = []
        if isinstance(filtered_articles_value, HumanMessage):
            try:
                message_content = json.loads(filtered_articles_value.content)
                articles_content = message_content.get('filtered_articles', [])
            except json.JSONDecodeError:
                print(f"Failed to parse filtered_articles_value content as JSON: {filtered_articles_value.content}")
        else:
            print(f"Unexpected type for filtered_articles_value: {type(filtered_articles_value)}")

        #print("Articles Content:", articles_content)  # Debugging line

        summaries = []
        for article in articles_content:
            article_str = json.dumps(article)
            #print(article_str, "\n")
            summarization_prompt = prompt.format(
                filtered_articles=article_str,
                keywords=keywords_value,
                feedback=feedback_value,
                datetime=get_current_utc_datetime()
            )

            messages = [
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": "Summarize the filtered RSS feed article."}
            ]

            llm = self.get_llm()
            ai_msg = llm.invoke(messages)
            response = ai_msg.content
            #print(response)

            try:
                # Parse the response to extract the summary
                response_data = json.loads(response)
                if 'summaries' in response_data and len(response_data['summaries']) > 0:
                    summaries.extend(response_data['summaries'])
                else:
                    raise ValueError("No valid summaries found in the response")
            except json.JSONDecodeError:
                print(f"Failed to parse response as JSON: {response}")
            except ValueError as e:
                print(f"Error processing summary: {str(e)}")

        final_response = {"summaries": summaries}
        # Create a HumanMessage object with the final response
        human_message_response = HumanMessage(content=json.dumps(final_response))

        # Update the state with the HumanMessage object
        self.update_state("summarization_response", human_message_response)

        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Summarizer: {json.dumps(final_response, indent=2)}\n")

        return self.state

import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from threading import Lock

class TokenBucket:
    def __init__(self, tokens, fill_rate):
        self.capacity = tokens
        self.tokens = tokens
        self.fill_rate = fill_rate
        self.last_check = time.time()
        self.lock = Lock()

    def get_token(self):
        with self.lock:
            now = time.time()
            time_passed = now - self.last_check
            self.tokens = min(self.capacity, self.tokens + time_passed * self.fill_rate)
            self.last_check = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    def wait_for_token(self):
        while not self.get_token():
            time.sleep(0.1)

class ReviewerAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adjust these values based on your API limits
        self.rate_limiter = TokenBucket(tokens=30, fill_rate=0.5)  # 30 tokens per minute

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def review_summary(self, summary, keywords, feedback_value, prompt):
        self.rate_limiter.wait_for_token()

        summary_str = json.dumps(summary)
        reviewer_prompt = prompt.format(
            summary=summary_str,
            keywords=keywords,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
            state=self.state
        )

        messages = [
            {"role": "system", "content": reviewer_prompt},
            {"role": "user", "content": "Review the summarized article for accuracy and relevance."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        review_data = json.loads(response)
        if 'review' in review_data:
            return review_data['review']
        else:
            raise ValueError("No valid review found in the response")

    def invoke(self, summaries, prompt=reviewer_prompt_template, feedback=None, keywords=None):
        feedback_value = feedback() if callable(feedback) else feedback
        summaries_value = summaries() if callable(summaries) else summaries
        feedback_value = check_for_content(feedback_value)

        # Extract content from HumanMessage object
        summaries_content = []
        if isinstance(summaries_value, HumanMessage):
            try:
                message_content = json.loads(summaries_value.content)
                summaries_content = message_content.get('summaries', [])
            except json.JSONDecodeError:
                print(f"Failed to parse summaries_value content as JSON: {summaries_value.content}")
        else:
            print(f"Unexpected type for summaries_value: {type(summaries_value)}")

        reviews = []
        for summary in summaries_content:
            try:
                review = self.review_summary(summary, keywords, feedback_value, prompt)
                reviews.append(review)
                # Small random delay between reviews
                time.sleep(random.uniform(0.5, 1))
            except Exception as e:
                print(f"Error processing review: {str(e)}")

        final_response = {"reviews": reviews}
        human_message_response = HumanMessage(content=json.dumps(final_response))

        self.update_state("reviewer_response", human_message_response)

        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Reviewer: {json.dumps(final_response, indent=2)}\n")

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
    def invoke(self, articles, summaries, feedback=None, prompt=report_generation_prompt_template):
        feedback_value = feedback() if callable(feedback) else feedback
        summaries_value = summaries() if callable(summaries) else summaries
        articles_value = articles() if callable(articles) else articles
        feedback_value = check_for_content(feedback_value)

        # Extract content from HumanMessage object
        summaries_content = []
        articles_content = []
        if isinstance(summaries_value, HumanMessage):
            try:
                message_content = json.loads(summaries_value.content)
                summaries_content = message_content.get('summaries', [])
            except json.JSONDecodeError:
                print(f"Failed to parse summaries_value content as JSON: {summaries_value.content}")
        else:
            print(f"Unexpected type for summaries_value: {type(summaries_value)}")

        if isinstance(articles_value, HumanMessage):
            try:
                message_content = json.loads(articles_value.content)
                articles_content = message_content.get('filtered_articles', [])
            except json.JSONDecodeError:
                print(f"Failed to parse articles_value content as JSON: {articles_value.content}")
        else:
            print(f"Unexpected type for articles_value: {type(articles_value)}")

        reports = []
        for article, summary in zip(articles_content, summaries_content):
            article_str = json.dumps(article)
            summary_str = json.dumps(summary)

            report_generation_prompt = prompt.format(
                article=article_str,
                summary=summary_str,
                feedback=feedback_value,
                datetime=get_current_utc_datetime()
            )

            messages = [
                {"role": "system", "content": report_generation_prompt},
                {"role": "user", "content": "Generate a concise report based on the article and its summary."}
            ]

            llm = self.get_llm()
            ai_msg = llm.invoke(messages)
            response = ai_msg.content

            try:
                # Parse the response to extract the report
                response_data = json.loads(response)
                if 'report' in response_data:
                    reports.append(response_data['report'])
                else:
                    raise ValueError("No valid report found in the response")
            except json.JSONDecodeError:
                print(f"Failed to parse response as JSON: {response}")
            except ValueError as e:
                print(f"Error processing report: {str(e)}")

        final_response = {"reports": reports}
        # Create a HumanMessage object with the final response
        human_message_response = HumanMessage(content=json.dumps(final_response))

        # Update the state with the HumanMessage object
        self.update_state("report_generation_response", human_message_response)

        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"Report Generator: {json.dumps(final_response, indent=2)}\n")

        return self.state

