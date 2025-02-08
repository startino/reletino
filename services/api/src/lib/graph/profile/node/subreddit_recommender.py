from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from src.interfaces.llm import gpt_4o_mini
from src.interfaces.reddit import get_reddit_instance
from src.lib.graph.profile.tools.subreddit import Subreddit
from src.lib.graph.profile.tools.web_scraper import web_scraper
from src.lib.graph.profile.tools.subreddit import search_relevant_subreddits
from src.lib.graph.profile.state import Context
from langchain_core.output_parsers import JSONOutputToolsParser
from langchain_core.messages import AIMessage
import json, uuid
import logging

class SubredditRecommendationOutput(BaseModel):
    reasoning: str
    subreddits: list[Subreddit]

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

class SubredditRecommender:
    def __init__(self, context: Context, objective: str):
        self.llm = gpt_4o_mini()
        self.context = context
        self.objective = objective
        if context.type == "url":
            self.context.value = web_scraper(context.value)

    async def __call__(self) -> SubredditRecommendationOutput:
        """Main function to analyze product and get recommendations"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Recommend subreddits based on the product information"),
            ("user", self.context.value)
        ])
        
        chain = prompt | self.llm.bind_tools([search_relevant_subreddits, SubredditRecommendationOutput], tool_choice="any") | JSONOutputToolsParser(return_id=True)
        recommendation = await chain.ainvoke({})
        
        result = parse_response(response=recommendation[0], name=self.name)            

        return {
            "messages": result
        }
    
    
    
    