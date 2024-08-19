# import json
# import yaml
# import os
from termcolor import colored
from models.openai_models import get_open_ai, get_open_ai_json
from models.ollama_models import OllamaModel, OllamaJSONModel
from models.vllm_models import VllmJSONModel, VllmModel
from models.groq_models import GroqModel, GroqJSONModel
from models.claude_models import ClaudVertexModel, ClaudVertexJSONModel
from models.gemini_models import GeminiModel, GeminiJSONModel
from langchain_core.messages import HumanMessage
import json
from datetime import datetime
from prompts.prompts import (
    summarization_prompt_template
)
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['FeedParser']  # This is your database name

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
            return ClaudVertexJSONModel(
                model=self.model,
                temperature=self.temperature
            ) if json_model else ClaudVertexModel(
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


class SummarizationAgent(Agent):
    def invoke(self, articles, keywords, feedback=None, prompt=summarization_prompt_template, batch_size=5):
        feedback_value = feedback() if callable(feedback) else feedback
        articles_value = articles() if callable(articles) else articles
        keywords_value = keywords() if callable(keywords) else keywords
        feedback_value = check_for_content(feedback_value)

        # Extract content from HumanMessage object
        articles_content = []
        if isinstance(articles_value, list) and len(articles_value) > 0 and isinstance(articles_value[0], HumanMessage):
            try:
                message_content = json.loads(articles_value[0].content)
                articles_content = message_content.get('articles', [])
            except json.JSONDecodeError:
                print(f"Failed to parse articles_value content as JSON: {articles_value[0].content}")
        else:
            print(f"Unexpected type for articles_value: {type(articles_value)}")

        all_summaries = []

        # Process articles in batches
        for i in range(0, len(articles_content), batch_size):
            batch = articles_content[i:i+batch_size]
            batch_str = json.dumps(batch)

            summarization_prompt = prompt.format(
                articles=batch_str,
                keywords=keywords_value,
                feedback=feedback_value,
                datetime=self.get_current_utc_datetime()
            )

            messages = [
                {"role": "system", "content": summarization_prompt},
                {"role": "user", "content": f"Summarize this batch of {len(batch)} articles."}
            ]

            llm = self.get_llm()
            ai_msg = llm.invoke(messages)
            response = ai_msg.content

            try:
                response_data = json.loads(response)
                if 'summaries' in response_data and len(response_data['summaries']) > 0:
                    all_summaries.extend(response_data['summaries'])

                    # Insert each summary into MongoDB
                    for summary in response_data['summaries']:
                        summarized_content = {
                            "scraped_content_id": summary['source'],  # This assumes source is the URL or ID
                            "summary": summary['summary']
                        }
                        db['SummarizedContent'].insert_one(summarized_content)  # Use the 'SummarizedContent' collection

                else:
                    print(f"No valid summaries found in the response for batch {i//batch_size + 1}")
            except json.JSONDecodeError:
                print(f"Failed to parse response as JSON for batch {i//batch_size + 1}: {response}")
            except ValueError as e:
                print(f"Error processing summaries for batch {i//batch_size + 1}: {str(e)}")

        final_response = {"summaries": all_summaries}
        human_message_response = HumanMessage(content=json.dumps(final_response))

        self.update_state("summarization_response", human_message_response)

        with open("D:/VentureInternship/response.txt", "a") as file:
            file.write(f"\nSummarizer: {json.dumps(final_response, indent=2)}\n")

        return self.state

    @staticmethod
    def get_current_utc_datetime():
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")