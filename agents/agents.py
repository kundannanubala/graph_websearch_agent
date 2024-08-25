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


class AnalysisNode2Agent(Agent):
    def invoke(self, state):
        # Correctly extract preprocessed data from state
        preprocessed_data_message = state["preprocessed_data"][0]
        preprocessed_data = json.loads(preprocessed_data_message.content)

        # Correctly extract analysis_node1 results from state
        analysis_node1_message = state["analysis_node1_response"][-1]
        analysis_node1_results = json.loads(analysis_node1_message.content)
        
        # Correctly extract knowledgeBase data from state
        knowledge_base_message = state["knowledge_base"][0]
        knowledge_base = json.loads(knowledge_base_message.content)        

        messages = [
            {"role": "system", "content": analysis_node2_prompt.format(
                text=preprocessed_data['text'],
                analysis_results=json.dumps(analysis_node1_results, indent=2),
                knowledge_base=json.dumps(knowledge_base,indent=2)
            )},
            {"role": "user", "content": "Please provide your analysis."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)

        # Store the result in the state
        if "analysis_node2_response" not in state:
            state["analysis_node2_response"] = []
        state["analysis_node2_response"].append(
            HumanMessage(role="system", content=ai_msg.content)
        )
        response=ai_msg.content
        with open('D:/VentureInternship/AI Agent/ProjectK/response.txt','a') as file:
            file.write(f"Analysis Node 2 response:\n{response}\n")

        return {"analysis_node2_response": state["analysis_node2_response"]}
    

class FeedbackGenerationAgent(Agent):
    def invoke(self, state):
        # Correctly extract preprocessed data from state
        preprocessed_data_message = state["preprocessed_data"][0]
        preprocessed_data = json.loads(preprocessed_data_message.content)

        # Correctly extract analysis_node1 results from state
        analysis_node1_message = state["analysis_node1_response"][-1]
        analysis_node1_results = json.loads(analysis_node1_message.content)

        # Correctly extract analysis_node2 results from state
        analysis_node2_message = state["analysis_node2_response"][-1]
        analysis_node2_results = json.loads(analysis_node2_message.content)
        
        # Correctly extract knowledgeBase data from state
        knowledge_base_message = state["knowledge_base"][0]
        knowledge_base = json.loads(knowledge_base_message.content) 

        messages = [
            {"role": "system", "content": feedback_generation_prompt.format(
                text=preprocessed_data['text'],
                analysis_results=json.dumps({**analysis_node1_results, **analysis_node2_results}, indent=2),
                knowledge_base=json.dumps(knowledge_base,indent=2)
            )},
            {"role": "user", "content": "Please provide your detailed feedback."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)

        # Store the result in the state
        if "feedback_response" not in state:
            state["feedback_response"] = []
        state["feedback_response"].append(
            HumanMessage(role="system", content=ai_msg.content)
        )
        response=ai_msg.content
        with open('D:/VentureInternship/AI Agent/ProjectK/response.txt','a') as file:
            file.write(f"FeedBack Node response:\n{response}\n")
        

        return {"feedback_response": state["feedback_response"]}   
    

class ScoringAgent(Agent):
    def invoke(self, state):
        # Correctly extract analysis_node1 results from state
        analysis_node1_message = state["analysis_node1_response"][-1]
        analysis_node1_results = json.loads(analysis_node1_message.content)

        # Correctly extract analysis_node2 results from state
        analysis_node2_message = state["analysis_node2_response"][-1]
        analysis_node2_results = json.loads(analysis_node2_message.content)
        
        # Correctly extract knowledgeBase data from state
        knowledge_base_message = state["knowledge_base"][0]
        knowledge_base = json.loads(knowledge_base_message.content) 

        messages = [
            {"role": "system", "content": scoring_prompt.format(
                analysis_results=json.dumps({**analysis_node1_results, **analysis_node2_results}, indent=2),
                knowledge_base=json.dumps(knowledge_base,indent=2)
            )},
            {"role": "user", "content": "Please provide the IELTS writing score breakdown."}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)

        # Store the result in the state
        if "scoring_response" not in state:
            state["scoring_response"] = []
        state["scoring_response"].append(
            HumanMessage(role="system", content=ai_msg.content)
        )
        response=ai_msg.content
        with open('D:/VentureInternship/AI Agent/ProjectK/response.txt','a') as file:
            file.write(f"Scoring Node response:\n{response}\n")
        

        return {"scoring_response": state["scoring_response"]}    
    

class ParaphrasingAgent(Agent):
    def invoke(self, state):
        try:
            # Correctly extract preprocessed data from state
            preprocessed_data_message = state["preprocessed_data"][0]
            preprocessed_data = json.loads(preprocessed_data_message.content)

            # Correctly extract scoring results from state
            scoring_message = state["scoring_response"][-1]
            scoring_results = json.loads(scoring_message.content)
            
            # Correctly extract knowledgeBase data from state
            knowledge_base_message = state["knowledge_base"][0]
            knowledge_base = json.loads(knowledge_base_message.content) 

            messages = [
                {"role": "system", "content": paraphrasing_prompt.format(
                    text=preprocessed_data['text'],
                    scores=json.dumps(scoring_results, indent=2),
                    knowledge_base=json.dumps(knowledge_base,indent=2)
                )},
                {"role": "user", "content": "Please provide the improved, Band 8 level paraphrased version."}
            ]

            llm = self.get_llm()
            ai_msg = llm.invoke(messages)

            # Attempt to parse the response as JSON
            try:
                response_content = json.loads(ai_msg.content)
            except json.JSONDecodeError:
                # If parsing fails, use the raw text
                response_content = {"raw_text": ai_msg.content}

            # Store the result in the state
            if "paraphrased_response" not in state:
                state["paraphrased_response"] = []
            state["paraphrased_response"].append(
                HumanMessage(role="system", content=json.dumps(response_content))
            )

            with open('D:/VentureInternship/AI Agent/ProjectK/response.txt','a') as file:
                file.write(f"Paraphrasing Node response:\n{json.dumps(response_content, indent=2)}\n")

            return {"paraphrased_response": state["paraphrased_response"]}

        except Exception as e:
            error_message = f"Error in ParaphrasingAgent: {str(e)}"
            print("ERROR", error_message)
            error_response = {"error": error_message}

            if "paraphrased_response" not in state:
                state["paraphrased_response"] = []
            state["paraphrased_response"].append(
                HumanMessage(role="system", content=json.dumps(error_response))
            )

            with open('D:/VentureInternship/AI Agent/ProjectK/response.txt','a') as file:
                file.write(f"Paraphrasing Node error:\n{json.dumps(error_response, indent=2)}\n")

            return {"paraphrased_response": state["paraphrased_response"]}