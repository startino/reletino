from datetime import datetime
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

from src.interfaces import db
from supabase import Client, create_client

from src.models.project import Project
from src.models import SavedSubmission
from src.lib.evaluate_relevance import evaluate_submission
from src.models import Evaluation
from src.interfaces.reddit import get_subreddits

load_dotenv()

current_directory = Path(__file__).resolve().parent

# Path to the sibling file
cache_filepath = current_directory / "cache"

# Set up the cache directory
cache = dc.Cache(cache_filepath)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RedditStreamWorker:
    def __init__(self, project: Project, team_name: str):
        self._running = False
        self.profile_id = project.profile_id
        self.project = project
        self.subreddits = get_subreddits(project.subreddits)
        self.supabase: Client = db.client()
        self.team_name = team_name
        logging.info(f"Initialized RedditStreamWorker for project: {self.project.id}")

    def start(self):
        self._running = True
        logging.info(f"Starting RedditStreamWorker for project: {self.project.id}")
        
        while self._running:
            for submission in self.subreddits.stream.submissions():
                logging.info(f"Processing submission: {submission.id}")

                # Skip if not a submission (for typing)
                if not isinstance(submission, Submission):
                    logging.info(f"Skipping non-submission object: {submission}")
                    continue

                # Avoid repeating posts using caching
                is_cached = cache.get(self.project.id+submission.id)
                if is_cached:
                    logging.info(f"Skipping cached submission: {submission.id}")
                    continue
                
                try:
                    evaluation, profile_insights = evaluate_submission(
                        submission=submission,
                        project_prompt=self.project.prompt,
                        team_name=self.team_name,
                        project_name=self.project.title,
                    )

                    if evaluation is None:
                        logging.error(f"Error evaluating submission: {submission.id}")
                        continue
                    
                    saved_submission = SavedSubmission(
                        author=submission.author.name,
                        submission_created_utc= datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        reddit_id=submission.id,
                        subreddit=submission.subreddit.display_name,
                        title=submission.title,
                        selftext=submission.selftext,
                        url=submission.url,
                        is_relevant=evaluation.is_relevant,
                        reasoning=evaluation.chain_of_thought,
                        profile_insights=profile_insights,
                    )
                    
                    # Check if submission already exists
                    existing_submission = self.supabase.table("submissions").select("*").eq("url", saved_submission.url).eq("project_id", self.project.id).execute()
                    
                    if len(existing_submission.data) > 0:
                        logging.info(f"Submission already exists: {saved_submission.url}")
                        continue

                    self.supabase.table("submissions").insert(
                        {
                            "profile_id": self.profile_id,
                            "project_id": self.project.id,
                            **saved_submission.dict(),
                            "is_relevant": evaluation.is_relevant,
                            "profile_insights": profile_insights or "",
                        }
                    ).execute()
                    
                    logging.info(f"Inserted new submission: {submission.id}")
                    
                    cache.set(submission.id, submission.id)
                    
                    # Update credits atomically using a direct decrement operation
                    try:
                        credits_update = self.supabase.rpc(
                            'decrement_credits',
                            {'user_id': self.profile_id}
                        ).execute()
                        
                        if not credits_update.data:
                            logging.error("No response data from credits update")
                            continue
                            
                        if len(credits_update.data) > 0 and credits_update.data[0].get('remaining_credits', 0) <= 0:
                            logging.info(f"No credits remaining for user: {self.profile_id}.")
                            self.stop()
                            break
                            
                    except Exception as e:
                        logging.error(f"Error updating credits: {str(e)}")
                        continue
                
                except Exception as e:
                    logging.error(f"Error processing submission {submission.id}: {str(e)}")
                    continue
        
    def stop(self):
        self._running = False
        stopped_project = self.supabase.table("projects").update({"running": False}).eq("id", self.project.id).execute()
        if stopped_project.data is None:
            logging.error(f"Error stopping project: {stopped_project.error}")
    
        logging.info(f"Stopping RedditStreamWorker for project: {self.project.id}")