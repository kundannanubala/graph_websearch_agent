analysis_node2_prompt = """
You are an expert IELTS examiner. Analyze the following text for task achievement and coherence. 
Consider the following:

1. Task Achievement:
   - Does the response fully address all parts of the task?
   - Is the position clear throughout the response?
   - Are the ideas well-developed with relevant examples?

2. Coherence and Cohesion:
   - Is the information logically organized?
   - Is there a clear progression of ideas?
   - Is there appropriate use of cohesive devices?

Use the relevant content in Knowledge Base during your analysis

Text to analyze:
{text}

Previous analysis results:
{analysis_results}

Knowledge Base:
{knowledge_base}

Provide a detailed analysis of task achievement and coherence, including specific examples from the text.
"""

analysis_node2_guided_json = {
    "type": "object",
    "properties": {
        "task_achievement": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 9},
                "comments": {"type": "string"}
            },
            "required": ["score", "comments"]
        },
        "coherence": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 9},
                "comments": {"type": "string"}
            },
            "required": ["score", "comments"]
        }
    },
    "required": ["task_achievement", "coherence"]
}

feedback_generation_prompt = """
As an IELTS writing expert, provide detailed feedback on the following text. 
Use the analysis results to guide your feedback. Focus on:

1. Grammar and vocabulary usage
2. Task achievement
3. Coherence and cohesion
4. Overall writing style

Use the relevant content in Knowledge Base for feedback

Text:
{text}

Analysis results:
{analysis_results}

Knowledge Base:
{knowledge_base}

Provide specific examples from the text and suggest improvements. 
Your feedback should be constructive and actionable.
"""

feedback_generation_guided_json = {
    "type": "object",
    "properties": {
        "grammar_vocabulary": {
            "type": "object",
            "properties": {
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
                "suggestions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["strengths", "weaknesses", "suggestions"]
        },
        "task_achievement": {
            "type": "object",
            "properties": {
                "comments": {"type": "string"},
                "suggestions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["comments", "suggestions"]
        },
        "coherence_cohesion": {
            "type": "object",
            "properties": {
                "comments": {"type": "string"},
                "suggestions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["comments", "suggestions"]
        },
        "overall_feedback": {"type": "string"}
    },
    "required": ["grammar_vocabulary", "task_achievement", "coherence_cohesion", "overall_feedback"]
}

scoring_prompt = """
As an IELTS examiner, provide a detailed score breakdown for the writing sample based on the following criteria:

1. Task Achievement
2. Coherence and Cohesion
3. Lexical Resource
4. Grammatical Range and Accuracy

Use the provided analysis results to inform your scoring. For each criterion, provide a score out of 9 and a brief justification.
Use the relevant content in Knowledge Base while scoring

Analysis results:
{analysis_results}

Knowledge Base:
{knowledge_base}

Provide the overall band score as well as individual scores for each criterion.
"""

scoring_guided_json = {
    "type": "object",
    "properties": {
        "task_achievement": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 9},
                "justification": {"type": "string"}
            },
            "required": ["score", "justification"]
        },
        "coherence_cohesion": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 9},
                "justification": {"type": "string"}
            },
            "required": ["score", "justification"]
        },
        "lexical_resource": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 9},
                "justification": {"type": "string"}
            },
            "required": ["score", "justification"]
        },
        "grammatical_range_accuracy": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 9},
                "justification": {"type": "string"}
            },
            "required": ["score", "justification"]
        },
        "overall_band_score": {"type": "number", "minimum": 0, "maximum": 9}
    },
    "required": ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range_accuracy", "overall_band_score"]
}

paraphrasing_prompt = """
As an expert IELTS writer, your task is to paraphrase and improve the given text to achieve an IELTS Band 8 standard. 
Focus on enhancing:

1. Task Achievement
2. Coherence and Cohesion
3. Lexical Resource
4. Grammatical Range and Accuracy

Use the relevant content in Knowledge Base while paraphrasing

Original text:
{text}

Current scores:
{scores}

Knowledge Base:
{knowledge_base}

Please provide:
1. A paraphrased version that addresses the weaknesses identified in the scoring, 
   while maintaining the original meaning and improving the overall quality to reach Band 8 standard.
2. A list of specific improvements made for each of the four focus areas.
3. Any overall comments on the improvements made.

Your response should be in JSON format as specified.
"""

paraphrasing_guided_json = {
    "type": "object",
    "properties": {
        "paraphrased_text": {"type": "string"},
        "improvements": {
            "type": "object",
            "properties": {
                "task_achievement": {"type": "array", "items": {"type": "string"}},
                "coherence_cohesion": {"type": "array", "items": {"type": "string"}},
                "lexical_resource": {"type": "array", "items": {"type": "string"}},
                "grammatical_range_accuracy": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range_accuracy"]
        },
        "overall_comments": {"type": "string"}
    },
    "required": ["paraphrased_text", "improvements", "overall_comments"]
}
