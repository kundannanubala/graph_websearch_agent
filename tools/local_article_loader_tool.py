# tools/local_article_loader_tool.py

import json
from langchain_core.messages import HumanMessage

def local_article_loader_tool(state):
    try:
        # Load the articles from the local file
        with open("D:/VentureInternship/articles_with_content.json", 'r') as file:
            articles_with_content = json.load(file)

        # Update state with the correct message structure
        state["local_article_loader_response"] = [
            HumanMessage(role="system", content=json.dumps(articles_with_content))
        ]

        print("Articles loaded successfully from local file.")
        return {"local_article_loader_response": state["local_article_loader_response"]}

    except FileNotFoundError:
        error_message = "Error: articles_with_content.json file not found."
        print(error_message)
        state["local_article_loader_response"] = [
            HumanMessage(role="system", content=json.dumps({"error": error_message}))
        ]
        return {"local_article_loader_response": state["local_article_loader_response"]}

    except json.JSONDecodeError:
        error_message = "Error: Unable to parse the articles_with_content.json file."
        print(error_message)
        state["local_article_loader_response"] = [
            HumanMessage(role="system", content=json.dumps({"error": error_message}))
        ]
        return {"local_article_loader_response": state["local_article_loader_response"]}