from praw import Reddit
from praw.models import Subreddits
from dotenv import load_dotenv
import os

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
        user_agent="relevantino bot by u/antopia_hk",
        username=REDDIT_USERNAME,
    )


def get_subreddits(subreddits: list[str]):
    
    subreddits_formatted: str = "+".join(subreddits)
    
    reddit = get_reddit_instance()

    print("Reddit sign in success! Username: ", reddit.user.me())

    subreddits: Subreddits = reddit.subreddit(subreddits_formatted)

    return subreddits
