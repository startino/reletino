from pydantic import BaseModel, Field

class CotResponse(BaseModel):
    """Response with reasoning for Reddit post/DM."""
    
    chain_of_thought: str = Field(
        description="Explain your thought process in crafting the response."
    )
    response: str = Field(
        description="The final response to be sent to the Reddit user"
    )