from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from src.interfaces.llm import gpt_4o_mini
from src.interfaces.reddit import get_reddit_instance
from src.lib.graph.profile.tools.subreddit import Subreddit
from src.lib.graph.profile.tools.web_scraper import web_scraper
from src.lib.graph.profile.tools.subreddit import search_relevant_subreddits
from src.lib.graph.profile.state import Context, ProfileState
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.messages import AIMessage
import json

class RecommendationOutput(BaseModel):
    product_name: str = Field(description="The name of the product")
    product_description: str = Field(description="The description of the product")
    subreddits: list[Subreddit] = Field(description="The subreddits that are recommended")
    filtering_prompt: str = Field(description="The filtering prompt for the subreddits")
    
class Drafter:
    def __init__(self, context: Context, objective: str):
        self.llm = gpt_4o_mini()
        self.context = context
        self.objective = objective
    async def __call__(self, state: ProfileState):
        """Main function to analyze product and get recommendations"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in product drafting. You are given a product and you need to draft a product description and subreddits that are relevant to the product.
             
             Guidelines for drafting:
             1. The product name should justify the context provided by the user
             2. The product description should be 1-2 sentences
             3. The subreddits should be 5-7 subreddits that are relevant to the product
             4. The subreddits should be relevant to the product and the context
            """),
            ("user", self.context.value)
        ])
        
        chain = prompt | self.llm.bind_tools([RecommendationOutput], tool_choice="any") | JsonOutputToolsParser(return_id=True)
        recommendation = (await chain.ainvoke({}))[0]
        
        recommendation["name"] = recommendation["type"]

        results = [
            AIMessage(
                tool_call_id=recommendation["id"],
                content=json.dumps(recommendation["args"]),
                name="drafter",
                tool_calls=[recommendation],
            )
        ]
        
        return {
            "messages": results
        }