import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from praw import Reddit
# from src.interfaces.llm import gpt_4o_mini
# from src.interfaces import reddit
import praw
import os
from dotenv import load_dotenv
from praw.models import Subreddit, Submission

from langchain.tools import tool

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")


def get_reddit_instance():
    return Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        password=REDDIT_PASSWORD,
        user_agent="reletino bot by u/antopia_hk",
        username=REDDIT_USERNAME,
    )


class Subreddit(BaseModel):
    name: str = Field(description="Name of the subreddit without the 'r/' prefix")
    description: str | None = Field(description="Description of the subreddit")

@tool
def search_relevant_subreddits(queries: list[str]) -> list[Subreddit]:
    """Get relevant subreddits for a product/service"""
    reddit = get_reddit_instance()
    
    subredditss = []
    
    for query in queries:
        subreddits = list(reddit.subreddits.search(query))[:10]
        subredditss.extend([Subreddit(name=subreddit.display_name, description=subreddit.public_description) for subreddit in subreddits])
    
    return subredditss

if __name__ == "__main__":
    print(search_relevant_subreddits(["Content Creation", "AI", "Job Search"]))

