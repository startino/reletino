from typing import Dict, List, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from bs4 import BeautifulSoup
import aiohttp
from pydantic import BaseModel, Field
import asyncio
from src.interfaces.llm import gpt_4o_mini
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FormField(BaseModel):
    label: str = Field(description="Label of the field")
    value: str = Field(description="Value to populate the field with", default="")
    description: str = Field(description="Description of the field")

class ProcessedWebsite(BaseModel):
    business_name: str = Field(description="Name of the product/service.")
    summary: str = Field(description="Brief summary of the product/service.")

class Action(BaseModel):
    reasoning: str = Field(description="Reasoning for the action taken.")
    action: Literal["fill_field", "finish"]
    field_label: str | None = Field(description="Label of the field to fill.")
    

class State(BaseModel):
    form: list[FormField]
    use_case: Literal["leads", "competition_research", "other"]
    processed_website: ProcessedWebsite | None = None
    current_field_label: str | None = None
    completed_field_labels: list[str] = []
    


async def autofill_form(use_case: Literal["leads", "competition_research", "other"], url: str, fields: list[FormField]) -> Dict[str, FormField]:
    """
    Main function to autofill a form based on website content
    
    Args:
        use_case: Purpose of the form filling according to the user
        url: Website URL to scrape
        fields: List of FormField objects
        
    Returns:
        Dict mapping field IDs to FormField objects with generated values
    """
    
    async def website_processing() -> ProcessedWebsite:
        """Scrape website content using BeautifulSoup"""
        logger.debug(f"Starting website processing for URL: {url}")
        
        async with aiohttp.ClientSession() as session:
            try:
                logger.debug("Making HTTP request")
                async with session.get(url) as response:
                    html = await response.text()
                    logger.debug(f"Got HTML response of length: {len(html)}")
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    page_content = soup.get_text()
                    logger.debug(f"Extracted text content of length: {len(page_content)}")
                    
                    # Use GPT-4o Mini to extract relevant content
                    logger.debug("Initializing GPT-4o Mini")
                    llm = gpt_4o_mini().with_structured_output(ProcessedWebsite)
                    
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", f"""
                        ### OBJECTIVE ###
                        Extract the name of the product/service and a brief summary of the content of the website.
                        
                        ### PURPOSE ###
                        The purpose is to understand the product/service and the business behind it in order to fill out a form.
                        The user has specified that the purpose for this project is {use_case}
                        """)
                        ,
                        ("user", f"Website content: {page_content}")
                    ])
                    
                    logger.debug("Sending content to LLM")
                    chain = prompt | llm
                    processed_website = await chain.ainvoke({})
                    logger.debug(f"Got LLM response: {processed_website}")
                    
                    return processed_website
                    
            except Exception as e:
                logger.error(f"Error processing website: {e}", exc_info=True)
                raise
    
    async def field_autocompleter(state: State):
        """Create a node for processing a single form field"""
        logger.debug(f"Processing field: {state.current_field_label}")
        
        llm = gpt_4o_mini().with_structured_output(FormField)
        logger.debug(f"Current state: {state}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are an AI assistant that fills form fields based on website content for {state.use_case}"),
            ("user", f"""
            Website Content:
            Business Name: {state.processed_website.business_name}
            Summary: {state.processed_website.summary}
            
            Field to fill: {state.current_field_label}
            Description: {state.form[state.current_field_label].description}
            """)
        ])

        chain = prompt | llm
        result = await chain.invoke({})
        logger.debug(f"Field completion result: {result}")
        return result
    
    async def verify_form(state: State) -> Literal["continue", "end"]:
        """Verify that the form is complete"""
        logger.debug(f"Verifying form completion. Completed fields: {state.completed_field_labels}")
        logger.debug(f"Total fields: {len(state.form)}")
        
        # Check if all fields are completed
        if len(state.completed_field_labels) == len(state.form):
            logger.debug("All fields completed, ending workflow")
            return END
        else:
            logger.debug("Form incomplete, continuing workflow")
            return "field_autocompleter"
    
    # Create graph
    workflow = StateGraph(State)
    
    workflow.add_node("route_next", route_next)
    workflow.add_node("field_autocompleter", field_autocompleter)
    workflow.add_node("verify", verify_form)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "verify",
        lambda x: x,  # Pass through the verify_form result
        {
            "end": END,
            "field_autocompleter": "field_autocompleter"
        }
    )
    
    workflow.add_edge("field_autocompleter", "verify")
    
    # Set entry point
    workflow.set_entry_point("route_next")
    
    # Add website content to inputs
    starting_state: State = State(
        use_case=use_case,
        url=url,
        form=fields,
        processed_website= await website_processing()
    )
    
    graph = workflow.compile()
    
    # Execute graph
    async for event in graph.astream_events(
        starting_state,
        version="v2"
    ):
        logger.debug(f"Event: {event}")
        
    return event.state

async def route_next(state: State) -> Action:
    """Route to next action based on form state"""
    logger.debug(f"Routing next action. Completed fields: {state.completed_field_labels}")
    remaining_fields = [field for field in state.form if field.label not in state.completed_field_labels]
    logger.debug(f"Remaining fields: {remaining_fields}")
    
    llm = gpt_4o_mini().with_structured_output(Action)
    
    prompt = (
        "You are an AI agent deciding how to fill a form based on website content.\n\n"
        "Website Content:\n"
        f"Business Name: {state.processed_website.business_name if state.processed_website else 'Not processed'}\n"
        f"Summary: {state.processed_website.summary if state.processed_website else 'Not processed'}\n\n"
        "Form Status:\n"
        f"Completed Fields: {state.completed_field_labels}\n"
        f"Remaining Fields: {[field.label for field in remaining_fields]}\n\n"
        "Choose your next action:\n"
        "1. Fill a specific field (action: 'fill_field')\n"
        "2. Finish if all fields are complete (action: 'finish')"
    )

    return await llm.ainvoke(prompt)

# Example usage:
if __name__ == "__main__":
    form_fields = [
        FormField(label="business name", description="Company name"),
        FormField(label="subreddits", description="Subreddits to post to"),
        FormField(label="target audience", description="Target audience/customer base")
    ]
    
    async def main():
        results = await autofill_form(
            "leads",
            "https://releti.no",
            fields=form_fields
        )
        print(results)
    
    asyncio.run(main())