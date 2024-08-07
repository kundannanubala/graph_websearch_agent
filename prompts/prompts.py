planner_prompt_template = """
You are a planner. Your responsibility is to create a comprehensive plan to fetch, filter, and summarize RSS feed articles based on user-defined keywords and websites.
Your plan should provide appropriate guidance for your team to use various tools effectively.

Focus on highlighting the most relevant RSS feed sources and keywords to start with, as other team members will use your suggestions to fetch and process the RSS feeds.

If you receive feedback, you must adjust your plan accordingly. Here is the feedback received:
Feedback: {feedback}

Current date and time:
{datetime}

Your response must take the following json format:

    "rss_sources": ["List of RSS feed URLs"],
    "keywords": ["List of keywords"],
    "overall_strategy": "The overall strategy to guide the RSS feed processing",
    "additional_information": "Any additional information to guide the process including other keywords or filters"
"""

planner_guided_json = {
    "type": "object",
    "properties": {
        "rss_sources": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "List of RSS feed URLs"
            }
        },
        "keywords": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "List of keywords"
            }
        },
        "overall_strategy": {
            "type": "string",
            "description": "The overall strategy to guide the RSS feed processing"
        },
        "additional_information": {
            "type": "string",
            "description": "Any additional information to guide the process including other keywords or filters"
        }
    },
    "required": ["rss_sources", "keywords", "overall_strategy", "additional_information"]
}

# xml_parser_prompt_template = """
# You are an XML parser. Your task is to extract relevant articles from the provided JSON content of RSS feeds.

# Here is the JSON content:
# {rss_feed_content}

# Your goal is to extract the articles and provide them in a structured format.

# Current date and time:
# {datetime}

# Your response must take the following JSON format:

#     {
#         "title": "Title of the article",
#         "summary": "Summary of the article",
#         "link": "URL of the article",
#         "author": "Author of the article",
#         "published_date": "Published date of the article",
#         "image_url": "Image URL of the article"
#     }
# """
# xml_parser_guided_json = {
#     "type": "object",
#     "properties": {
#         "articles": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "title": {
#                         "type": "string",
#                         "description": "Title of the article"
#                     },
#                     "summary": {
#                         "type": "string",
#                         "description": "Summary of the article"
#                     },
#                     "link": {
#                         "type": "string",
#                         "description": "URL of the article"
#                     },
#                     "author": {
#                         "type": "string",
#                         "description": "Author of the article"
#                     },
#                     "published_date": {
#                         "type": "string",
#                         "description": "Published date of the article"
#                     },
#                     "image_url": {
#                         "type": "string",
#                         "description": "Image URL of the article"
#                     }
#                 },
#                 "required": ["title", "summary", "link", "author", "published_date"]
#             }
#         }
#     },
#     "required": ["articles"]
# }


keyword_filter_prompt_template = """
You are an advanced keyword filter and content analyzer. Your task is to intelligently filter the provided articles based on the user-defined keywords.

Articles to analyze: {articles}

Keywords to filter by: {keywords}

Your primary goal is to identify and return only the articles that contain any of the specified keywords in their title, summary, or content. Additionally:

1. Prioritize articles where keywords appear in the title or early in the summary.
2. Consider the relevance and context of the keyword usage, not just exact matches.
3. If a keyword is part of a larger word or phrase, assess if it's still relevant to the intended meaning.
4. Take into account synonyms or closely related terms to the provided keywords.
5. Ensure the filtered articles are recent and relevant to the current date and time.

Current date and time: {datetime}

Your response must take the following JSON format exactly as specified:

{{
    "filtered_articles": [
        {{
            "title": "Exact title of the article",
            "link": "Exact link of the article",
            "author": "Exact author of the article",
            "published_date": "Exact published date of the article"
        }}
    ]
}}

Ensure that your response is well-formatted and easily parseable JSON. Include only the most relevant articles that best match the filtering criteria.
"""
keyword_filter_guided_json = {
    "type": "object",
    "properties": {
        "filtered_articles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the article"
                    },
                    "link": {
                        "type": "string",
                        "description": "Link of the article"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author of the article"
                    },
                    "published_date": {
                        "type": "string",
                        "description": "Published date of the article"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the article"
                    }
                },
                "required": ["title", "link", "author", "published_date", "content"]
            }
        }
    },
    "required": ["filtered_articles"]
}


summarization_prompt_template = """
You are a summarizer. Your task is to create a concise summary of the filtered article from the RSS feed based entirely on the "content" of the article.

Here is the filtered article:
{filtered_articles}

Keywords to highlight: {keywords}

Generate a summary for the article. Ensure the summary captures the key points and main ideas. Do not deviate from the relevant information in the content. Highlight the usage of the relevant keyword that the article is associated with.

Adjust your summary based on any feedback received:
Feedback: {feedback}

Current date and time:
{datetime}

Your response must take the following json format:
{{
    "summaries": [
        {{
            "title": "Title of the article",
            "summary": "Concise summary of the article, highlighting the relevant keyword",
            "source": "URL of the article"
        }}
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


reviewer_prompt_template = """
You are an expert summary reviewer. Your task is to evaluate the quality of a single summary generated by the summarization process, not to reassess the filtering of articles.

Summary to review: {summary}

Keywords used for filtering: {keywords}

Previous feedback: {feedback}

Current date and time: {datetime}

State of the agents: {state}

Important guidelines:
1. Focus on the quality of the summary, not the initial article selection.
2. Assume the filtered article is relevant; your job is to review the summary of this article.
3. Not all keywords need to appear in the summary.
4. Evaluate if the summary effectively captures the main points of the article related to the given keywords.
5. Consider clarity, conciseness, and comprehensiveness within the context of the filtered article.

Your review should assess:
- Comprehensiveness: Does the summary capture the main points of the article?
- Relevance: Is the summary focused on aspects related to the given keywords?
- Clarity and Conciseness: Is the summary easy to understand and appropriately brief?

Your response must take the following JSON format:

{{
    "review": {{
        "feedback": "Provide specific feedback on the quality of the summary. If improvements are needed, offer clear suggestions.",
        "pass_review": true/false,
        "relevant_to_topic": true/false,
        "clear_and_concise": true/false,
        "valuable_information": true/false
    }}
}}

Remember, your role is to improve the summary, not to question the article selection process.
"""

reviewer_guided_json = {
    "type": "object",
    "properties": {
        "feedback": {
            "type": "string",
            "description": "Your feedback here. Provide specific feedback on the quality and relevance of the summary. If improvements are needed, offer constructive suggestions."
        },
        "pass_review": {
            "type": "boolean",
            "description": "True if the summary meets the quality standards, False otherwise."
        },
        "relevant_to_topic": {
            "type": "boolean",
            "description": "True if the summary is relevant to the main topic and some of the keywords, False otherwise."
        },
        "clear_and_concise": {
            "type": "boolean",
            "description": "True if the summary is well-written and easy to understand, False otherwise."
        },
        "valuable_information": {
            "type": "boolean",
            "description": "True if the summary provides useful insights related to the topic, False otherwise."
        }
    },
    "required": ["feedback", "pass_review", "relevant_to_topic", "clear_and_concise", "valuable_information"]
}


router_prompt_template = """
You are a router. Your task is to route the conversation to the next agent based on the feedback provided by the reviewer.
You must choose one of the following agents: planner, xml_parser, keyword_filter, summarization, or final_report.

Here is the feedback provided by the reviewer:
Feedback: {feedback}

### Criteria for Choosing the Next Agent:
- **planner**: If new information or adjustments to the overall strategy are required.
- **xml_parser**: If there are issues with parsing the RSS feed content.
- **keyword_filter**: If there are issues with filtering the articles based on keywords.
- **summarization**: If the summaries need improvement or adjustments.
- **report_generator**: If the feedback marks pass_review as True, you must select report_generator.

You must provide your response in the following json format:
    
    "next_agent": "one of the following: planner/xml_parser/keyword_filter/summarization/report_generator"
"""

router_guided_json = {
    "type": "object",
    "properties": {
        "next_agent": {
            "type": "string",
            "description": "one of the following: planner/xml_parser/keyword_filter/summarization/final_report"
        }
    },
    "required": ["next_agent"]
}

report_generation_prompt_template = """
You are a report generator. Your task is to generate a concise report based on a single article and its summary.

Here is the article information:
{article}

Here is the summary of the article:
{summary}

The report should include:
1. A brief introduction that provides context about the article topic.
2. A detailed section for the article including the title, summary, author, published date, and a link to the full article.
3. A short conclusion that highlights the key insights from the article.

Adjust your report based on any feedback received:
Feedback: {feedback}

Current date and time: {datetime}

Your response must take the following json format:

{{
    "report": {{
        "introduction": "Brief introduction to the article topic",
        "article": {{
            "title": "Title of the article",
            "summary": "Summary of the article",
            "author": "Author of the article",
            "published_date": "Published date of the article",
            "link": "URL of the article",
            "image_url": "Image URL of the article"
        }},
        "conclusion": "Short conclusion highlighting key insights"
    }}
}}
"""

report_generation_guided_json = {
    "type": "object",
    "properties": {
        "report": {
            "type": "object",
            "properties": {
                "introduction": {
                    "type": "string",
                    "description": "Brief introduction to the article topic"
                },
                "article": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the article"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Summary of the article"
                        },
                        "author": {
                            "type": "string",
                            "description": "Author of the article"
                        },
                        "published_date": {
                            "type": "string",
                            "description": "Published date of the article"
                        },
                        "link": {
                            "type": "string",
                            "description": "URL of the article"
                        },
                        "image_url": {
                            "type": "string",
                            "description": "Image URL of the article"
                        }
                    },
                    "required": ["title", "summary", "author", "published_date", "link"]
                },
                "conclusion": {
                    "type": "string",
                    "description": "Short conclusion highlighting key insights"
                }
            },
            "required": ["introduction", "article", "conclusion"]
        }
    },
    "required": ["report"]
}



