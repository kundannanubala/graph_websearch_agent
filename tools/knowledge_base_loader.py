import json
from langchain_core.messages import HumanMessage

from langchain_core.messages import HumanMessage
import json

def knowledge_base_loader(state):
    try:
        # Read the content of the file
        with open('D:/VentureInternship/AI Agent/ProjectK/knowledge_base.txt', 'r', encoding='utf-8') as file:
            knowledge_base_content = file.read()

        # Create a new knowledge base list
        new_knowledge_base = [
            HumanMessage(role="system", content=json.dumps({"knowledge_base": knowledge_base_content}))
        ]

        # Log the action
        with open("D:/VentureInternship/AI Agent/ProjectK/response.txt", "a") as log_file:
            log_file.write(f"\nKnowledge Base Loader: Loaded knowledge base\n")

        # Return the new knowledge base as an update to the state
        return {"knowledge_base": new_knowledge_base}

    except Exception as e:
        error_message = f"Error loading knowledge base: {str(e)}"
        print(error_message)

        # Log the error
        with open("D:/VentureInternship/AI Agent/ProjectK/response.txt", "a") as log_file:
            log_file.write(f"\nKnowledge Base Loader Error: {error_message}\n")

        # Return an error state
        return {"error": error_message}