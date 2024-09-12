from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional
from uuid import uuid4, UUID

from src.models.evaluated_submission import Evaluation


class SavedSubmission(BaseModel):
    """
    A Reddit submission that has been saved to the database.
    It's a variation of the EvaluatedSubmission but with the submission
    expanded to include the title and body.
    """
    author: str
    submission_created_utc: int
    reddit_id: str
    subreddit: str
    title: str
    selftext: str
    url: str