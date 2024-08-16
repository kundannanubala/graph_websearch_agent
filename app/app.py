from agent_graph.graph import create_graph, compile_workflow

# server = 'ollama'
# model = 'llama3:instruct'
# model_endpoint = None

server = 'claude'
model = "claude-3-5-sonnet@20240620"
model_endpoint = None
# server = 'openai'
# model = "gpt-4o"
# model_endpoint = None

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
        "https://rss.app/feeds/PfSPW1PZmIDrjC8u.xml", #https://www.greenbiz.com/
        "https://rss.app/feeds/bovDvfqaIz2KoDdw.xml", #https://www.green.earth
        "https://rss.app/feeds/qKjOEYXW4oEP6xYP.xml",
"https://rss.app/feeds/56HKOZAvi3Ym1tm7.xml",
"https://rss.app/feeds/uZLwiQhErv8b4yEK.xml",
"https://rss.app/feeds/K2enb0duBnv1BgXn.xml",
"https://rss.app/feeds/YqqGCKRoUgtzQxse.xml",
"https://rss.app/feeds/AlOYwfMt50xeeAGX.xml",
"https://rss.app/feeds/4zjgvZfHGaKwST6D.xml",



"https://rss.app/feeds/kiUZxHmxtC36zRK8.xml",
"https://rss.app/feeds/7RTOJmMmRAUs6sXX.xml",
"https://rss.app/feeds/yNLjX7f9gjYpz83D.xml",
"https://rss.app/feeds/hvRNY4LdKfAGnz2r.xml",
"https://rss.app/feeds/UhvBRMGqNUHB1WtF.xml"
"https://rss.app/feeds/efZhUMWNNHbxolMl.xml",
"https://rss.app/feeds/lNrrcxPKFtlKa1eY.xml"
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



    