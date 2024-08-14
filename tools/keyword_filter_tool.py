import json
from langchain_core.messages import HumanMessage
import re

def keyword_filter_tool(state):
    filtered_articles = []
    keywords = state.get("keywords", [])

    # Compile regex patterns for each keyword
    keyword_patterns = {keyword: re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE) for keyword in keywords}

    # Extract articles from the content scraper response
    for message in state["local_article_loader_response"]:
        if isinstance(message, HumanMessage):
            articles = json.loads(message.content).get("articles", [])

            for article in articles:
                title = article.get("title", "")
                content = article.get("content", "")

                # Combine title and content for searching
                full_text = f"{title}\n{content}"

                # Check which keywords match in the full text
                matching_keywords = [keyword for keyword, pattern in keyword_patterns.items() if pattern.search(full_text)]

                if matching_keywords:
                    filtered_article = article.copy()
                    filtered_article["matching_keywords"] = matching_keywords
                    filtered_articles.append(filtered_article)

    filtered_articles_json = {"filtered_articles": filtered_articles}

    # Store the filtered articles into a file
    with open("D:/VentureInternship/filtered_articles.json", 'w') as file:
        json.dump(filtered_articles_json, file, indent=4)

    with open("D:/VentureInternship/response.txt", "a") as file:
        file.write(f"\nKeyword_Filter_Tool: {len(filtered_articles)} articles filtered")
        for article in filtered_articles:
            file.write(f"\n  - Article: {article.get('title', 'No title')} | Keywords: {', '.join(article['matching_keywords'])}")

    # Update state with the correct message structure
    state["keyword_filter_response"] = [
        HumanMessage(role="system", content=json.dumps(filtered_articles_json))
    ]

    return {"keyword_filter_response": state["keyword_filter_response"]}