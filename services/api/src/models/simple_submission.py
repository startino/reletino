from pydantic import BaseModel

class SimpleSubmission(BaseModel):
    title: str
    selftext: str
    author_name: str
