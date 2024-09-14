from pydantic import BaseModel


class Project(BaseModel):
    id: str
    profile_id: str
    prompt: str
    subreddits: list[str]