from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID


class SavedSubmission(BaseModel):
    author: str
    submission_created_utc: str
    reddit_id: str
    subreddit: str
    title: str
    selftext: str
    url: str
    is_relevant: bool
    reasoning: str
