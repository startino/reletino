from pydantic import BaseModel, Field
from typing import Literal, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class Context(BaseModel):
    type: Literal["link", "description"] = Field(description="The type of the context")
    value: str = Field(description="The value of the context")

class ProfileState(BaseModel):
    context: Context
    objective: str = Field(description="The objective of the profile")
    messages: Annotated[list[BaseMessage], add_messages] = []
