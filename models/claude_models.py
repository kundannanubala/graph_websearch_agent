import os
from google.cloud import aiplatform
from anthropic import AnthropicVertex
from utils.helper_functions import load_config
from langchain_core.messages.human import HumanMessage
import json
from dotenv import load_dotenv
import re

load_dotenv()

class ClaudVertexModel:
    def __init__(self, temperature=0, model=None):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        load_config(config_path)

        # Load Google Cloud credentials
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.region = os.getenv("GOOGLE_CLOUD_REGION")

        # Initialize Anthropic Vertex client
        self.client = AnthropicVertex(project_id=self.project_id, region=self.region)

        self.temperature = temperature
        self.model = model

    def invoke(self, messages):
        system = messages[0]["content"]
        user = messages[1]["content"]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
            )

            response_content = response.content[0].text
            response_formatted = HumanMessage(content=response_content)

            return response_formatted
        except Exception as e:
            error_message = f"Error in invoking model! {str(e)}"
            print("ERROR", error_message)
            response = {"error": error_message}
            response_formatted = HumanMessage(content=json.dumps(response))
            return response_formatted

class ClaudVertexJSONModel(ClaudVertexModel):
    def invoke(self, messages):
        system = messages[0]["content"]
        user = messages[1]["content"]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": f"system:{system}. Your output must be json formatted. Just return the specified json format, do not prepend your response with anything. \n\n user:{user}"
                    }
                ]
            )
            response_content = response.content[0].text
            with open('D:/VentureInternship/AI Agent/ProjectK/ModelResponse.txt','a') as file:
                file.write(f'Model Response:\n{response_content}\n')

            # Clean the response content
            cleaned_content = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', response_content)

            try:
                response = json.loads(cleaned_content)
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                response = {"raw_text": cleaned_content}

            with open('D:/VentureInternship/AI Agent/ProjectK/ModelResponse.txt','a') as file:
                file.write(f'Json Load Response:\n{response}\n')

            response = json.dumps(response)
            with open('D:/VentureInternship/AI Agent/ProjectK/ModelResponse.txt','a') as file:
                file.write(f'Json Dumps Response:\n{response}\n')

            response_formatted = HumanMessage(content=response)

            return response_formatted
        except Exception as e:
            error_message = f"Error in invoking model! {str(e)}"
            print("ERROR", error_message)
            response = {"error": error_message}
            response_formatted = HumanMessage(content=json.dumps(response))
            return response_formatted