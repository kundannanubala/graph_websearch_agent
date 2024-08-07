from agent_graph.graph import create_graph, compile_workflow

# server = 'ollama'
# model = 'llama3:instruct'
# model_endpoint = None

server = 'openai'
model = 'gpt-4o'
model_endpoint = None

# server = 'vllm'
# model = 'meta-llama/Meta-Llama-3-70B-Instruct' # full HF path
# model_endpoint = 'https://kcpqoqtjz0ufjw-8000.proxy.runpod.net/' 
# #model_endpoint = runpod_endpoint + 'v1/chat/completions'
# stop = "<|end_of_text|>"

iterations = 40

print ("Creating graph and compiling workflow...")
graph = create_graph(server=server, model=model, model_endpoint=model_endpoint)
workflow = compile_workflow(graph)
print ("Graph and workflow created.")


if __name__ == "__main__":

    verbose = False

    while True:
        query = input("Enter to continue: ")
        if query.lower() == "exit":
            break

        rss_urls = [
        # "https://rss.app/feeds/PfSPW1PZmIDrjC8u.xml" #https://www.greenbiz.com/
        "https://rss.app/feeds/bovDvfqaIz2KoDdw.xml" #https://www.green.earth
    ]

        keywords = ["tokenization", "web3", "RWA", "AI", "Biodiversity", "nature based carbon credits"]
        
        dict_inputs = {
            "rss_urls": rss_urls,
            "keywords": keywords
        }
        # thread = {"configurable": {"thread_id": "4"}}
        limit = {"recursion_limit": iterations}

        # for event in workflow.stream(
        #     dict_inputs, thread, limit, stream_mode="values"
        #     ):
        #     if verbose:
        #         print("\nState Dictionary:", event)
        #     else:
        #         print("\n")

        for event in workflow.stream(
            dict_inputs, limit
            ):
            if verbose:
                # print("\nState Dictionary:", event)
                print('')
            else:
                print("\n")



    