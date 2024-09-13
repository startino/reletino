from pydantic import BaseModel


class Project(BaseModel):
    project_id: str
    prompt: str
    subreddits: list[str]