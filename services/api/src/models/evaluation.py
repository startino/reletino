from langchain_core.pydantic_v1 import BaseModel, Field

class Evaluation(BaseModel):
    chain_of_thought: str = Field(description="Use this field for logical reasoning to decide if this submission is relevant irrelevant.")
    is_relevant: bool = Field(description="Final conclusion whether the post is relevant or irrelevant.")
