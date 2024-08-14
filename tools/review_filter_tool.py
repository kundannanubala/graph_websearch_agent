import json
from langchain_core.messages import HumanMessage

def review_filter_tool(state):
    filtered_articles = []
    filtered_summaries = []

    # Extract the reviewer response
    reviewer_response = state.get("reviewer_response", [])
    if reviewer_response and isinstance(reviewer_response[-1], HumanMessage):
        reviews = json.loads(reviewer_response[-1].content).get("reviews", [])
    else:
        print("No valid reviewer response found.")
        return state

    # Extract the keyword filter response
    keyword_filter_response = state.get("keyword_filter_response", [])
    if keyword_filter_response and isinstance(keyword_filter_response[-1], HumanMessage):
        articles = json.loads(keyword_filter_response[-1].content).get("filtered_articles", [])
    else:
        print("No valid keyword filter response found.")
        return state

    # Extract the summarization response
    summarization_response = state.get("summarization_response", [])
    if summarization_response and isinstance(summarization_response[-1], HumanMessage):
        summaries = json.loads(summarization_response[-1].content).get("summaries", [])
    else:
        print("No valid summarization response found.")
        return state

    # Create a set of titles that passed the review
    passed_titles = {review["title"] for review in reviews if review.get("pass_review", False)}

    # Filter articles and summaries
    for article in articles:
        if article["title"] in passed_titles:
            filtered_articles.append(article)

    for summary in summaries:
        if summary["title"] in passed_titles:
            filtered_summaries.append(summary)

    # Update the state with filtered results
    state["keyword_filter_response"] = [HumanMessage(content=json.dumps({"filtered_articles": filtered_articles}))]
    state["summarization_response"] = [HumanMessage(content=json.dumps({"summaries": filtered_summaries}))]

    # Log the results
    with open("D:/VentureInternship/response.txt", "a") as file:
        file.write(f"\nReview Filter Tool: Removed {len(articles) - len(filtered_articles)} articles that failed review.\n")

    return state