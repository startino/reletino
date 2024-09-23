from langchain_core.pydantic_v1 import BaseModel, Field

class Evaluation(BaseModel):
    reasoning: str = Field(description="Use logical reasoning to explain why you determined this post is relevant or irrelevant.")
    is_relevant: bool = Field(description="Final conclusion whether the post is relevant or irrelevant.")
    
