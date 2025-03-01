from pydantic import BaseModel, Field


class RedditComment(BaseModel):
    comment: str = Field(description="the text of the reddit comment")
    # Not sure if this should be a model or simply a string.


class GenerateCommentRequest(BaseModel):
    title: str
    selftext: str
    instructions: str = ""
