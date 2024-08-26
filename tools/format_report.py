import json
import re
from datetime import datetime
from langchain_core.messages import HumanMessage

def format_report(state):
    try:
        # Extract all relevant messages from the state
        analysis_node1 = next((msg for msg in state["messages"] if msg.role == "analysis_node1"), None)
        analysis_node2 = next((msg for msg in state["messages"] if msg.role == "analysis_node2"), None)
        feedback = next((msg for msg in state["messages"] if msg.role == "feedback_generation"), None)
        scoring = next((msg for msg in state["messages"] if msg.role == "scoring"), None)
        paraphrasing = next((msg for msg in state["messages"] if msg.role == "paraphrasing"), None)

        # Initialize the formatted report
        formatted_report = "IELTS Writing Task Analysis Report\n"
        formatted_report += "=" * 40 + "\n"
        formatted_report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Add Analysis Results
        formatted_report += "Analysis Results:\n"
        formatted_report += "-" * 40 + "\n"
        if analysis_node1:
            formatted_report += f"Analysis Node 1:\n{json.dumps(json.loads(analysis_node1.content), indent=2)}\n\n"
        if analysis_node2:
            formatted_report += f"Analysis Node 2:\n{json.dumps(json.loads(analysis_node2.content), indent=2)}\n\n"

        # Add Feedback
        if feedback:
            formatted_report += "Feedback:\n"
            formatted_report += "-" * 40 + "\n"
            formatted_report += f"{json.dumps(json.loads(feedback.content), indent=2)}\n\n"

        # Add Scores
        if scoring:
            formatted_report += "Scores:\n"
            formatted_report += "-" * 40 + "\n"
            formatted_report += f"{json.dumps(json.loads(scoring.content), indent=2)}\n\n"

        # Add Paraphrased Content
        if paraphrasing:
            formatted_report += "Paraphrased Content:\n"
            formatted_report += "-" * 40 + "\n"
            paraphrased_content = json.loads(paraphrasing.content)
            if isinstance(paraphrased_content, dict) and "paraphrased_text" in paraphrased_content:
                formatted_report += f"{paraphrased_content['paraphrased_text']}\n\n"
            else:
                formatted_report += f"{json.dumps(paraphrased_content, indent=2)}\n\n"

        # Write the formatted report to report.txt
        with open('D:/VentureInternship/AI Agent/ProjectK/report.txt', 'w', encoding='utf-8') as file:
            file.write(formatted_report)

        print("Report generated successfully and saved to report.txt")

        # Add the formatted report to the state
        state["messages"].append(
            HumanMessage(role="formatted_report", content=formatted_report)
        )

        return {"messages": state["messages"]}

    except Exception as e:
        error_message = f"Error generating report: {str(e)}"
        print(error_message)
        return {"error": error_message}