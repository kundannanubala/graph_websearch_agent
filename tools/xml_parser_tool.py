import feedparser
import json
from datetime import datetime
from termcolor import colored
from langchain_core.messages import HumanMessage

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
                    "summary": entry.get("summary", "No Summary"),
                    "link": entry.get("link", "No Link"),
                    "author": entry.get("author", "Unknown Author"),
                    "published_date": entry.get("published", "Unknown Date"),
                    "image_url": entry.get("media_thumbnail", [{"url": "No Image"}])[0].get("url", "No Image") if "media_thumbnail" in entry else "No Image"
                }
                articles.append(article)
        except Exception as e:
            print(colored(f"Failed to fetch or parse RSS feed from {url}: {e}", 'red'))

    parsed_articles = {"articles": articles}
    with open("D:/VentureInternship/response.txt", "a") as file:
        file.write(f"\nXML_parser_Tool")
    
    # Update state with the correct message structure
    state["xml_parser_response"].append(
        HumanMessage(role="system", content=json.dumps(parsed_articles))
    )
    return {"xml_parser_response" : state["xml_parser_response"]}
