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
    current_action: Action | None = None


async def autofill_form(use_case: Literal["leads", "competition_research", "other"], url: str, fields: list[FormField]) -> list[FormField]:
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
        logger.debug(f"Processing field: {state.current_action.field_label}")
        
        llm = gpt_4o_mini().with_structured_output(FormField)
        logger.debug(f"Current state: {state}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are an AI assistant that fills form fields based on website content for {state.use_case}"),
            ("user", f"""
            Website Content:
            Business Name: {state.processed_website.business_name}
            Summary: {state.processed_website.summary}
            
            Field to fill: {state.current_action.field_label}
            Description: {next((field.description for field in state.form if field.label == state.current_action.field_label), "No description found")}
            """)
        ])

        chain = prompt | llm
        result = await chain.ainvoke({})
        logger.debug(f"Field completion result: {result}")
        
        updated_form = [
            result if field.label == result.label else field
            for field in state.form
        ]
        
        return { "form": updated_form }

    async def supervisor(state: State) -> Action:
        """Route to next action based on form state"""
        logger.debug(f"Routing next action. Completed fields: {[field.label for field in state.form]}")
        remaining_fields = [field for field in state.form if field.value == ""]
        logger.debug(f"Remaining fields: {remaining_fields}")
        
        llm = gpt_4o_mini().with_structured_output(Action)
        
        prompt = (
            "You are an AI agent deciding how to fill a form based on website content.\n\n"
            "Website Content:\n"
            f"Business Name: {state.processed_website.business_name if state.processed_website else 'Not processed'}\n"
            f"Summary: {state.processed_website.summary if state.processed_website else 'Not processed'}\n\n"
            "Form Status:\n"
            f"Current Form: {[field for field in state.form]}\n"
            "Choose your next action:\n"
            "1. Fill a specific field (action: 'fill_field')\n"
            "2. Finish if all fields are complete (action: 'finish')"
        )

        return { "current_action": await llm.ainvoke(prompt) }
    
    # Create graph
    workflow = StateGraph(State)
    
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("field_autocompleter", field_autocompleter)
    
    def routing_function(state: State) -> Literal["fill_field", "finish"]:  
        if state.current_action.action != "finish":
            return "try_again"
        
        # Check if all fields are completed
        if all(field.value != "" for field in state.form):
            logger.info("All fields completed, ending workflow")
            return END # can route to a verification agent to review the form before submitting in the future
        else:
            logger.info("Form incomplete, continuing workflow")
            return "try_again"
    
    workflow.add_conditional_edges(
        "supervisor",
        routing_function,
        {
            "try_again": "field_autocompleter",
            END: END
        }
    )
    
    workflow.add_edge(
        "field_autocompleter",
        "supervisor"
    )

    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add website content to inputs
    starting_state: State = State(
        use_case=use_case,
        url=url,
        form=fields,
        processed_website= await website_processing()
    )
    
    graph = workflow.compile()
    
    # Execute graph
    async for event in graph.astream(starting_state, stream_mode="values"):
        final_state = State(**event)
        
    return final_state.form


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
            "https://monday.com",
            fields=form_fields
        )
        print(results)
    
    asyncio.run(main())