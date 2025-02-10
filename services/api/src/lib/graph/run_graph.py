from src.lib.graph.profile import ProfileGraph
from src.lib.graph.profile.state import ProfileState, Context
from src.lib.graph.profile.tools.web_scraper import web_scraper
from src.lib.graph.profile.node.drafter import RecommendationOutput
import json

async def run():
    context = Context(
        type="url",
        value="https://starti.no/"
    )

    if context.type == "url":
        context.value = f"# URL: \n{context.value}" + f"## URL DATA: \n{web_scraper(context.value)}"
    
    initial_state = ProfileState(
        context=context,
        objective="find_leads",
        messages=[],  
    )
    
    graph = ProfileGraph(initial_state).graph()
  
    final_state = await graph.ainvoke(initial_state)
    
    parsed_results = RecommendationOutput(**final_state["messages"][-1].tool_calls[0]["args"])
    return parsed_results
    

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(run())
    print("Results: \n\n")
    print("Product Name:", results.product_name)
    print("Product Description:", results.product_description)
    print("\nRecommended Subreddits:")
    for subreddit in results.subreddits:
        print(f"Name: {subreddit.name}")
        print(f"Description: {subreddit.description}")
    print("\nFiltering Prompt: ", results.filtering_prompt)