import json
from pprint import pprint
from praw import Reddit
from praw.models import Subreddits, Submission
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import diskcache as dc
import logging

from pathlib import Path

from supabase import Client, create_client

from src.models import SavedSubmission
from src.evaluate_relevance import evaluate_submission
from src.models import Evaluation
from src.reddit_utils import get_subreddits, get_reddit_instance

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


current_directory = Path(__file__).resolve().parent

# Path to the sibling file
cache_filepath = current_directory / "cache"

# Set up the cache directory
cache = dc.Cache(cache_filepath)


class RedditStreamWorker:
    def __init__(self, project_id: str, prompt: str, subreddits: list[str], username: str, password: str):
        self._running = False
        self.subreddits = get_subreddits(subreddits, username, password)

    def start(self):
        self._running = True
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        while self._running:
    
            if not REDDIT_USERNAME or not REDDIT_PASSWORD:
                raise TypeError("couldnt find username or password in env vars")

            for submission in self.subreddits.stream.submissions():

                # Skip if not a submission (for typing)
                if not isinstance(submission, Submission):
                    continue

                # Avoid repeating posts using caching
                is_cached = cache.get(submission.id)
                if is_cached:
                    continue
                
                evaluation: Evaluation = evaluate_submission(submission=submission)
                
                saved_submission = SavedSubmission(
                    author=submission.author.name,
                    submission_created_utc=submission.created_utc,
                    reddit_id=submission.id,
                    subreddit=submission.subreddit.display_name,
                    title=submission.title,
                    selftext=submission.selftext,
                    url=submission.url,
                )
                                              
                # Check if submission already exists
                existing_submission = supabase.table("submissions").select("*").eq("url", saved_submission.url).execute()

                if len(existing_submission.data) > 0:
                    return

                supabase.table("submissions").insert(
                    {
                        # please don't ask me why only one is using model_dump
                        # somehow evaluation is a dict already??
                        # anyone better with Python typing pls help :pray:
                        **json.loads(json.dumps(saved_submission.model_dump(), default=str)),
                        **json.loads(json.dumps(evaluation, default=str)),
                    }
                ).execute()
                
                cache.set(submission.id, submission.id)                    
                
    def stop(self):
        self._running = False
