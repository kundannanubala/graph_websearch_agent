from langchain_core.messages import HumanMessage
import json

def knowledge_base_loader(state):
    try:
        # Read the content of the file
        with open('D:/VentureInternship/AI Agent/ProjectK/knowledge_base.txt', 'r', encoding='utf-8') as file:
            knowledge_base_content = file.read()

        # Create a new knowledge base message
        knowledge_base_message = HumanMessage(
            role="knowledgeBase", 
            content=json.dumps({"knowledge_base": knowledge_base_content})
        )

        # Add the message to the state
        state["messages"].append(knowledge_base_message)

        # Log the action
        with open("D:/VentureInternship/AI Agent/ProjectK/response.txt", "w") as log_file:
            log_file.write(f"\nKnowledge Base Loader: Loaded knowledge base\n")

        return {"messages": state["messages"]}

    except Exception as e:
        error_message = f"Error loading knowledge base: {str(e)}"
        print(error_message)

        # # Log the error
        # with open("response.txt", "a") as log_file:
        #     log_file.write(f"\nKnowledge Base Loader Error: {error_message}\n")

        # Return an error state
        return {"error": error_message}