from langchain_core.pydantic_v1 import BaseModel, Field

class Evaluation(BaseModel):
    is_relevant: bool = Field(description="Determines if the post is relevant.")
    reason: str = Field(description="Explain why you determined this post is relevant or irrelevant. Format: Post is [answer] because [reason]. Hence, it is not a lead and not relevant")
