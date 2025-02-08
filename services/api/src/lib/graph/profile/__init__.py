from src.lib.graph.profile.state import Context, ProfileState
from langgraph.graph import END, START, StateGraph
from src.lib.graph.profile.node.subreddit_recommender import SubredditRecommender
from src.lib.graph.profile.node.drafter import Drafter
from langgraph.prebuilt import ToolNode
from src.lib.graph.profile.tools.subreddit import search_relevant_subreddits

class ProfileGraph:
    def __init__(self, objective: str):
        self.objective = objective
        self.context = Context
        
    def graph(self, state: ProfileState):
        workflow = StateGraph(ProfileState)
        
        drafter = Drafter(context=state.context, objective=self.objective)
        subreddit_recommender = SubredditRecommender(context=state.context, objective=self.objective)
        
        workflow.add_node(
            "subreddit_recommender",
            subreddit_recommender
        )
        
        workflow.add_node(
            "drafter",
            drafter
        )
        
        workflow.add_node(
            "tools",
            ToolNode(
                [search_relevant_subreddits]
            )
        )
        
        def should_continue(state: ProfileState):
            last_msg = state.messages[-1]
            
            if last_msg.tool_calls:
                if "reasoning" in last_msg.tool_calls[0]["args"]:
                    return "tools"
                else:
                    return "drafter"
            else:
                return "drafter"
            
        
        workflow.add_edge(START, "subreddit_recommender")
        workflow.add_conditional_edges(
            "subreddit_recommender", should_continue, ["tools", "drafter"]
        )
        
        workflow.add_edge("tools", "subreddit_recommender")
        workflow.add_edge("drafter", END)
        
        return workflow.compile()
    
    