from pydantic import BaseModel

class Evaluation(BaseModel):
    is_relevant: bool
    reason: str | None = None
