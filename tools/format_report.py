import json
import re
from datetime import datetime

def format_report():
    try:
        # Read the content from response.txt
        with open('D:/VentureInternship/AI Agent/ProjectK/response.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split the content into sections
        sections = re.split(r'\n(?=\w+ Node response:)', content)

        # Initialize the formatted report
        formatted_report = "IELTS Writing Task Analysis Report\n"
        formatted_report += "=" * 40 + "\n"
        formatted_report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        analysis_results = {}
        feedback = {}
        scores = {}
        paraphrased_content = ""

        for section in sections:
            if "Node response:" in section:
                node_name, node_content = section.split(":", 1)
                node_name = node_name.strip()

                try:
                    parsed_content = json.loads(node_content.strip())

                    if "Analysis Node" in node_name:
                        analysis_results.update(parsed_content)
                    elif "FeedBack Node" in node_name:
                        feedback = parsed_content
                    elif "Scoring Node" in node_name:
                        scores = parsed_content
                    elif "Paraphrasing Node" in node_name:
                        paraphrased_content = parsed_content.get("paraphrased_text", "")

                except json.JSONDecodeError:
                    # If it's not JSON, just store the content as is
                    if "Analysis Node" in node_name:
                        analysis_results[node_name] = node_content.strip()
                    elif "FeedBack Node" in node_name:
                        feedback[node_name] = node_content.strip()
                    elif "Scoring Node" in node_name:
                        scores[node_name] = node_content.strip()
                    elif "Paraphrasing Node" in node_name:
                        paraphrased_content = node_content.strip()

        # Format and add analysis results
        formatted_report += "Analysis Results:\n"
        formatted_report += "-" * 40 + "\n"
        for key, value in analysis_results.items():
            formatted_report += f"{key}:\n{json.dumps(value, indent=2)}\n\n"

        # Format and add feedback
        formatted_report += "Feedback:\n"
        formatted_report += "-" * 40 + "\n"
        for key, value in feedback.items():
            if isinstance(value, dict):
                formatted_report += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list):
                        formatted_report += f"  {sub_key}:\n"
                        for item in sub_value:
                            formatted_report += f"    - {item}\n"
                    else:
                        formatted_report += f"  {sub_key}: {sub_value}\n"
            else:
                formatted_report += f"{key}: {value}\n"
        formatted_report += "\n"

        # Format and add scores
        formatted_report += "Scores:\n"
        formatted_report += "-" * 40 + "\n"
        for key, value in scores.items():
            if isinstance(value, dict):
                formatted_report += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    formatted_report += f"  {sub_key}: {sub_value}\n"
            else:
                formatted_report += f"{key}: {value}\n"
        formatted_report += "\n"

        # Add paraphrased content
        formatted_report += "Paraphrased Content:\n"
        formatted_report += "-" * 40 + "\n"
        formatted_report += paraphrased_content + "\n\n"

        # Add suggestions for improvement
        if isinstance(feedback, dict) and "improvements" in feedback:
            formatted_report += "Suggestions for Improvement:\n"
            formatted_report += "-" * 40 + "\n"
            for category, suggestions in feedback["improvements"].items():
                formatted_report += f"{category.capitalize()}:\n"
                for suggestion in suggestions:
                    formatted_report += f"  - {suggestion}\n"
            formatted_report += "\n"

        # Write the formatted report to report.txt
        with open('D:/VentureInternship/AI Agent/ProjectK/report.txt', 'w', encoding='utf-8') as file:
            file.write(formatted_report)

        print("Report generated successfully and saved to report.txt")
        return {"formatted_report": [formatted_report]}

    except Exception as e:
        error_message = f"Error generating report: {str(e)}"
        print(error_message)
        return {"error": error_message}

# You can call this function in your main workflow
# result = format_report()