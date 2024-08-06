import requests
from bs4 import BeautifulSoup
import json
from termcolor import colored
from langchain_core.messages import HumanMessage

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = "\n".join([para.get_text() for para in paragraphs])
        return content
    except requests.RequestException as e:
        print(colored(f"Failed to scrape content from {url}: {e}", 'red'))
        return None

def content_scraper_tool(state):
    articles_with_content = []
    
    # Extracting parsed articles from state["xml_parser_response"]
    for message in state["xml_parser_response"]:
        parsed_articles = json.loads(message.content)["articles"]
        for article in parsed_articles:
            if 'link' in article:
                print(colored(f"Scraping URL: {article['link']}", 'blue'))
                content = scrape_website(article['link'])
                if content:
                    article['content'] = content
                    articles_with_content.append(article)
                    print(colored(f"Content scraped for: {article['link']}", 'green'))
                else:
                    print(colored(f"No content found for: {article['link']}", 'yellow'))
            else:
                print(colored(f"No link found in article: {article}", 'red'))

    articles_with_content_json = {"articles": articles_with_content}
    
    # Store the articles with content into a file
    with open("D:/VentureInternship/articles_with_content.json", 'w') as file:
        json.dump(articles_with_content_json, file, indent=4)
    with open("D:/VentureInternship/response.txt", "a") as file:
        file.write(f"\nContent_Scraper_Tool")

    # Update state with the correct message structure
    state["content_scraper_response"].append(
        HumanMessage(role="system", content=json.dumps(articles_with_content_json))
    )
    return {"content_scraper_response": state["content_scraper_response"]}