from pydantic import BaseModel, Field
from typing import Literal, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class Context(BaseModel):
    type: Literal["link", "description"] = Field(description="The type of the context")
    value: str = Field(description="The value of the context")

class ProfileState(BaseModel):
    context: Context
    objective: Literal["find_leads", "find_competitors", "find_ideas", "find_influencers", "find_investors", "find_partners"] = Field(description="The objective of the profile")
    messages: Annotated[list[BaseMessage], add_messages] = []
    mode: Literal["standard", "advanced"] = Field(description="The mode of the profile")
