from typing import Optional
from praw.models import Submission
from pydantic import BaseModel, ConfigDict

class Evaluation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    is_relevant: bool
    reason: str | None = None
    qualifying_question: str | None = None
