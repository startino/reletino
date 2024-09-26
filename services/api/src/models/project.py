from pydantic import BaseModel


class Project(BaseModel):
    id: str
    title: str
    profile_id: str
    prompt: str
    subreddits: list[str]
    running: bool | None = None
