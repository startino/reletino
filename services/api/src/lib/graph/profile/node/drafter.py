from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from src.interfaces.llm import gpt_4o_mini
from src.interfaces.reddit import get_reddit_instance
from src.lib.graph.profile.tools.subreddit import Subreddit
from src.lib.graph.profile.tools.web_scraper import web_scraper
from src.lib.graph.profile.tools.subreddit import search_relevant_subreddits
from src.lib.graph.profile.state import Context


class RecommendationOutput(BaseModel):
    product_name: str
    product_description: str
    subreddits: list[Subreddit]
    filtering_prompt: str
    

class Drafter:
    def __init__(self, context: Context, objective: str):
        self.llm = gpt_4o_mini()
        self.context = context
        self.objective = objective
        if context.type == "url":
            self.context.value = web_scraper(context.value)

    async def __call__(self) -> RecommendationOutput:
        """Main function to analyze product and get recommendations"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract product information from website content"),
            ("user", self.context.value)
        ])
        
        chain = prompt | self.llm.with_structured_output(RecommendationOutput)
        recommendation = await chain.ainvoke({})
        
        return recommendation