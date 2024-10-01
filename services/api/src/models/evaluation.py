from langchain_core.pydantic_v1 import BaseModel, Field

class Evaluation(BaseModel):
    reasoning: str = Field(description="Use this field for logical reasoning to decide if this submission is relevant irrelevant. Do this step by step. This field should evaluate each choice fairly and not bias towards any.")
    is_relevant: bool = Field(description="Final conclusion whether the post is relevant or irrelevant.")
