import requests
from bs4 import BeautifulSoup
from states.state import AgentGraphState
from langchain_core.messages import HumanMessage

def scrape_ubersuggest(keyword):
    url = f"https://app.neilpatel.com/en/ubersuggest/keyword_ideas?keyword={keyword}&lang=en&country=us"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example: Extract keyword suggestions
    keyword_suggestions = []
    for div in soup.find_all('div', class_='suggestion-title'):
        keyword_suggestions.append(div.text.strip())

    return keyword_suggestions

def keyword_research_tool(state: AgentGraphState, keyword):
    try:
        keyword_data = scrape_ubersuggest(keyword)
        state["keyword_research_response"].append(HumanMessage(role="system", content=str({"keyword_suggestions": keyword_data})))
        return state
    except requests.RequestException as e:
        state["keyword_research_response"].append(HumanMessage(role="system", content=f"error fetching keyword data: {e}"))
        return state
