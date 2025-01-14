from pydantic import BaseModel

class RedditUserProfile(BaseModel):
    username: str
    comment_karma: int
    link_karma: int
    total_karma: int
    created_utc: float
    is_mod: bool
    is_gold: bool
    posts: list[dict]
    comments: list[dict]