from pydantic import BaseModel, Field
from typing import Literal, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class Context(BaseModel):
    type: Literal["url", "text"]
    value: str

class ProfileState(BaseModel):
    context: Context
    objective: str
    messages: Annotated[list[BaseMessage], add_messages] = []
