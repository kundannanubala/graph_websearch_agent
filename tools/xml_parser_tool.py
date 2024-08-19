import feedparser
import json
from datetime import datetime
from termcolor import colored
from pymongo import MongoClient
from langchain_core.messages import HumanMessage

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if it's different
db = client['FeedParser']  # This is your database name

def xml_parser_tool(rss_feed_urls, state):
    # Fetch and parse the content of each RSS feed URL
    articles = []
    for url in rss_feed_urls:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(colored(f"Failed to parse RSS feed from {url}: {feed.bozo_exception}", 'red'))
                continue

            for entry in feed.entries:
                article = {
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "No Link"),
                    "author": entry.get("author", "Unknown Author"),
                    "published_date": entry.get("published", "Unknown Date"),
                }
                articles.append(article)

                # Insert the parsed article into MongoDB
                parsed_article = {
                    "title": article['title'],
                    "link": article['link'],
                    "author": article['author'],
                    "published_date": article['published_date'],
                    "url_id": url  # You can manage URL references more effectively
                }
                db['ParsedArticles'].insert_one(parsed_article)  # Use the 'ParsedArticles' collection

        except Exception as e:
            print(colored(f"Failed to fetch or parse RSS feed from {url}: {e}", 'red'))

    parsed_articles = {"articles": articles}

    # Store parsed_articles into a file (for your existing process)
    with open("D:/VentureInternship/parsed_articles.json", 'w') as file:
        json.dump(parsed_articles, file, indent=4)
    with open("D:/VentureInternship/response.txt", "w") as file:
        file.write(f"\nXML_parser_Tool")
    
    # Update state with the correct message structure
    state["xml_parser_response"].append(
        HumanMessage(role="system", content=json.dumps(parsed_articles))
    )
    return {"xml_parser_response": state["xml_parser_response"]}
