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
    analysis_node2_prompt,
    feedback_generation_prompt,
    scoring_prompt,
    paraphrasing_prompt
)
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState
from pymongo import MongoClient

# # MongoDB connection setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client['FeedParser']  # This is your database name

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


class FlexibleAgent(Agent):
    def __init__(self, state: AgentGraphState, role_name: str, model=None, server=None, temperature=0, model_endpoint=None, stop=None, guided_json=None):
        super().__init__(state, model, server, temperature, model_endpoint, stop, guided_json)
        self.role_name = role_name

    def invoke(self, state, prompt_template, required_variables, user_content):
        # Extract required variables from state
        variables = {}
        for var in required_variables:
            content = next((msg.content for msg in state["messages"] if msg.role == var), None)
            if content is None:
                raise ValueError(f"Missing required data: {var}")
            variables[var] = json.loads(content)

        # Prepare the variables for the prompt template
        prompt_variables = {}

        # Handle all variables
        for var, content in variables.items():
            if var == 'preprocessing' and 'text' in content:
                prompt_variables['text'] = content['text']
            elif var == 'knowledgeBase' and 'knowledge_base' in content:
                prompt_variables['knowledge_base'] = content['knowledge_base']
            elif var in ['analysis_node1', 'analysis_node2']:
                if 'analysis_results' not in prompt_variables:
                    prompt_variables['analysis_results'] = {}
                prompt_variables['analysis_results'].update(content)
            else:
                prompt_variables[var] = content

        # Convert analysis_results to JSON string
        if 'analysis_results' in prompt_variables:
            prompt_variables['analysis_results'] = json.dumps(prompt_variables['analysis_results'], indent=2)

        # Format the prompt
        try:
            system_content = prompt_template.format(**prompt_variables)
        except KeyError as e:
            raise KeyError(f"Missing key in prompt template: {e}. Available keys: {prompt_variables.keys()}")

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)

        # Log the response
        with open("D:/VentureInternship/AI Agent/ProjectK/response.txt", 'a') as file:
            file.write(f'\n{self.role_name} response:{ai_msg.content}\n')

        # Update the state with the agent's response using the correct role name
        state["messages"].append(
            HumanMessage(role=self.role_name, content=ai_msg.content)
        )

        # Return the updated state
        return {"messages": state["messages"]}