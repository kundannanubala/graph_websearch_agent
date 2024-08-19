summarization_prompt_template = """
You are a summarizer. Your task is to create concise summaries of the articles from the RSS feed based entirely on the "content" of each article.

Here are the articles:
{articles}

Keywords to highlight: {keywords}

Generate a summary for each article. Ensure each summary captures the key points and main ideas. Do not deviate from the relevant information in the content. Highlight the usage of the relevant keyword that each article is associated with.

Adjust your summaries based on any feedback received:
Feedback: {feedback}

Current date and time: {datetime}

Your response must take the following json format:
{{
    "summaries": [
        {{
            "title": "Title of the article",
            "summary": "Concise summary of the article, highlighting the relevant keyword",
            "source": "URL of the article"
        }},
        ...
    ]
}}
"""

summarization_guided_json = {
    "type": "object",
    "properties": {
        "summaries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the article"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Concise summary of the article, highlighting the relevant keyword"
                    },
                    "source": {
                        "type": "string",
                        "description": "URL of the article"
                    }
                },
                "required": ["title", "summary", "source"]
            }
        }
    },
    "required": ["summaries"]
}