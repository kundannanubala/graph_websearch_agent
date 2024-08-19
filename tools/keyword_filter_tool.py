import json
from langchain_core.messages import HumanMessage
import re
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['FeedParser']  # This is your database name

def keyword_filter_tool(state):
    filtered_articles = []
    keywords = state.get("keywords", [])

    # Compile regex patterns for each keyword
    keyword_patterns = {keyword: re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE) for keyword in keywords}

    # Extract articles from the content scraper response
    for message in state["content_scraper_response"]:
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

                    # Insert the filtered article into MongoDB
                    filtered_article_db = {
                        "keyword_ids": matching_keywords,  # This assumes keyword_ids are the keywords themselves; adjust as needed
                        "scraped_content_id": article['link'],  # You can manage this reference better if using ObjectIds
                    }
                    db['FilteredArticles'].insert_one(filtered_article_db)  # Use the 'FilteredArticles' collection

    filtered_articles_json = {"filtered_articles": filtered_articles}

    # Store the filtered articles into a file (for your existing process)
    with open("D:/VentureInternship/filtered_articles.json", 'w') as file:
        json.dump(filtered_articles_json, file, indent=4)

    with open("D:/VentureInternship/response.txt", "a") as file:
        file.write(f"\nKeyword_Filter_Tool: {len(filtered_articles)} articles filtered\n")
        for article in filtered_articles:
            file.write(f"\n  - Article: {article.get('title', 'No title')} | Keywords: {', '.join(article['matching_keywords'])}")

    # Update state with the correct message structure
    state["keyword_filter_response"] = [
        HumanMessage(role="system", content=json.dumps(filtered_articles_json))
    ]

    return {"keyword_filter_response": state["keyword_filter_response"]}
