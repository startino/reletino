from pydantic import BaseModel

class Evaluation(BaseModel):
    is_relevant: bool
    reasoning: str | None = None
