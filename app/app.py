import tkinter as tk
from tkinter import simpledialog, messagebox
from agent_graph.graph import create_graph, compile_workflow

# Server and model configuration
server = 'claude'
model = "claude-3-5-sonnet@20240620"
model_endpoint = None

iterations = 40

print("Creating graph and compiling workflow...")
graph = create_graph(server=server, model=model, model_endpoint=model_endpoint)
workflow = compile_workflow(graph)
print("Graph and workflow created.")

def get_user_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("IELTS Writing Analyzer", "Enter your IELTS writing task:", parent=root)
    return user_input

def show_results(results):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Analysis Results", results)

if __name__ == "__main__":
    verbose = False

    while True:
        user_input = get_user_input()
        if user_input is None or user_input.lower() == "exit":
            break

        dict_inputs = {
            "user_input": user_input
        }

        limit = {"recursion_limit": iterations}

        print("\nAnalyzing your writing...")
        final_event = None
        for event in workflow.stream(dict_inputs, limit):
            final_event = event
            if verbose:
                print(event)
            else:
                print(".", end="", flush=True)

        print("\nAnalysis complete.")

        should_continue = messagebox.askyesno("Continue?", "Would you like to analyze another piece of writing?")
        if not should_continue:
            break

print("Thank you for using the IELTS Writing Analyzer!")