from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from src.interfaces.llm import gpt_o1, gpt_4o
from src.interfaces.reddit import get_reddit_instance
from src.lib.graph.project_setup.tools.subreddit import Subreddit
from src.lib.graph.project_setup.tools.web_scraper import web_scraper
from src.lib.graph.project_setup.tools.subreddit import search_relevant_subreddits
from src.lib.graph.project_setup.state import ProfileState, Context
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.messages import AIMessage
import json, uuid
import logging

class SubredditRecommendationOutput(BaseModel):
    reasoning: str = Field(description="The reasoning behind the subreddit recommendation")
    subreddits: list[Subreddit] = Field(description="The subreddits that are recommended")

def parse_response(response: dict[str, str], name: str) -> list[AIMessage]:
    """
    Parse the response from the model, where a response is a Pydantic tool.
    Currently only supports one Response tool call per message. (noticable by "parsed_responses[0]")
    """

    response_tool_calls = [tc for tc in response["args"] if "reasoning" in tc]

    response["name"] = response["type"]
    return [
        AIMessage(
            tool_call_id=response["id"],
            content=json.dumps(response["args"]),
            name=name,
            tool_calls=[response] if not response_tool_calls else [],
        )
    ]

def get_model_for_mode(mode: str):
    if mode == "advanced":
        return gpt_o1()
    return gpt_4o()

class SubredditRecommender:
    def __init__(self, state: ProfileState):
        self.llm = get_model_for_mode(state.mode)
        self.context = state.context
        self.objective = state.objective

    async def __call__(self, state: ProfileState):
        """Main function to analyze product and get recommendations"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized subreddit recommendation expert. Your task is to recommend relevant subreddits based on the provided product/service information.

                    Guidelines for recommendations:
                    1. Recommend 7-15 subreddits that are likely to be active and have a substantial user base
                    2. Focus on both direct industry/niche subreddits and adjacent communities where prospects might be
                    3. Consider the following factors:
                    - Product/service type and industry
                    - Target audience demographics
                    - User pain points and needs
                    - Related technologies or solutions
                    - Professional/business context if B2B
                    - Consumer interests if B2C

                    For each subreddit, provide:
                    - Subreddit name (without r/ prefix)
                    - A brief explanation of why it's relevant

                    Avoid:
                    - Extremely broad subreddits (e.g., r/all, r/popular)
                    - Off-topic or loosely related subreddits"""),
            ("user", self.context.value)
        ])
        
        chain = prompt | self.llm.bind_tools([search_relevant_subreddits, SubredditRecommendationOutput], tool_choice="any") | JsonOutputToolsParser(return_id=True)
        recommendation = await chain.ainvoke({})
        
        result = parse_response(response=recommendation[0], name="subreddit_recommender")            

        return {
            "messages": result
        }
    
    
    
    