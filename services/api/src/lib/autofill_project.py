from typing import Dict, List, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from bs4 import BeautifulSoup
import aiohttp
from pydantic import BaseModel, Field
import asyncio
from src.interfaces.llm import gpt_4o_mini

class FormField(BaseModel):
    label: str = Field(description="Label of the field")
    value: str = Field(description="Value to populate the field with")
    description: str = Field(description="Description of the field")

class ProcessedWebsite(BaseModel):
    business_name: str = Field(description="Name of the product/service.")
    summary: str = Field(description="Brief summary of the product/service.")

class Action(BaseModel):
    reasoning: str = Field(description="Reasoning for the action taken.")
    action: Literal["fill_field", "finish"]
    field_label: str | None = Field(description="Label of the field to fill.")
    

class State(BaseModel):
    form: Dict[str, FormField]
    use_case: Literal["leads", "competition_research", "other"]
    processed_website: ProcessedWebsite | None = None
    current_field_label: str | None = None
    completed_fields: Dict[str, FormField] = {}
    


async def autofill_form(use_case: Literal["leads", "competition_research", "other"], url: str, form_fields: Dict[str, str]) -> Dict[str, FormField]:
    """
    Main function to autofill a form based on website content
    
    Args:
        use_case: Purpose of the form filling according to the user
        url: Website URL to scrape
        form_fields: Dict mapping field IDs to descriptions
        
    Returns:
        Dict mapping field IDs to FormField objects with generated values
    """
    
    async def website_processing(use_case: Literal["leads", "competition_research", "other"], url: str) -> ProcessedWebsite:
        """Scrape website content using BeautifulSoup"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Get text content
                    page_content = soup.get_text()
                    
                    # Use GPT-4o Mini to extract relevant content
                    llm = gpt_4o_mini().with_structured_output(ProcessedWebsite)
                    
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", f"""
                        ### OBJECTIVE ###
                        Extract the name of the product/service and a brief summary of the content of the website.
                        
                        ### PURPOSE ###
                        The purpose is to understand the product/service and the business behind it in order to fill out a form.
                        The user has specified that the purpose for this project is {use_case}
                        
                        ### CONTEXT ###
                        - The name should be a single sentence.
                        - The summary should be a concise description of the website's content.
                        
                        ### STYLE ###
                        - The title and summary should be in plain text, not markdown.
                        - The summary should be concise but detailed. Using short sentences to describe the website with a lot of details.
                        """)
                        ,
                        ("user", f"Website content: {page_content}")
                    ])
                    
                    chain = prompt | llm
                    processed_website = await chain.invoke({})
                    
                    return processed_website
                    
            except Exception as e:
                print(f"Error scraping website: {e}")
                raise
    
    # Scrape website
    processed_website = await website_processing(use_case, url)
    
    def field_autocompleter(state: State):
        """Create a node for processing a single form field"""
        
        llm = gpt_4o_mini().with_structured_output(FormField)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an AI assistant that fills form fields based on website content for a specific project.
            The purpose of this project is for {state.use_case}, according to the user.
            """),
            ("user", f"""
            Website Content:
            Business Name: {state.processed_website.business_name}
            Summary: {state.processed_website.summary}
            
            Field to fill:
            Label: {state.current_field_label}
            Description: {state.form[state.current_field_label].description}
            
            Consider the relationships between this field and any completed fields: {state.completed_fields}
            """)
        ])
    
        chain = prompt | llm
        return chain
    
    
    # Create graph
    workflow = StateGraph(State)
    
    # Add nodes for website processing and field filling
    workflow.add_node("website_processing", website_processing)
    workflow.add_node("field_autocomplete", field_autocompleter)
    
    # Add conditional edges based on router
    workflow.add_conditional_edges(
        "website_processing",
        lambda state: route_next(state),
        {
            "finish": END,
            "fill_field": "field_autocomplete" 
        }
    )

    workflow.add_conditional_edges(
        "field_autocomplete",
        lambda state: route_next(state), 
        {
            "finish": END,
            "fill_field": "field_autocomplete"
        }
    )

    # Set entry point
    workflow.set_entry_point("website_processing")
    
    graph = workflow.compile()
    
    # Add website content to inputs
    starting_state = {
        "use_case": use_case,
        "url": url,
        "form": form_fields
    }
    
    # Execute graph
    results = await graph.ainvoke(starting_state)
    
    return results

def route_next(state: State) -> Action:
    """Route to next action based on form state"""
    
    llm = gpt_4o_mini().with_structured_output(Action)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI agent deciding how to fill a form based on website content.
        You will decide to either:
        1. Fill a specific field (action: "fill_field") 
        2. Finish if all fields are complete (action: "finish")
        
        When filling fields:
        - Explain the step by step reasoning that leads to your decision
        - Choose fields that are not yet completed
        - Consider relationships between fields
        - Fill fields in a logical order
        - Ensure that the label of the field is accurate without any typos
        """),
        ("user", f"""
        Website Content:
        Business Name: {state.processed_website.business_name if state.processed_website else 'Not processed'}
        Summary: {state.processed_website.summary if state.processed_website else 'Not processed'}
        
        Form Status:
        Completed Fields: {state.completed_fields}
        Remaining Fields: {set(state.form.keys()) - set(state.completed_fields.keys())}
        
        Choose your next action:
        1. Fill a specific field (action: "fill_field")
        2. Finish if all fields are complete (action: "finish")
        """)
    ])
    
    chain = prompt | llm
    return chain.invoke()

# Example usage:
if __name__ == "__main__":
    form_fields = {
        "company_name": "Company name",
        "description": "Brief company description", 
        "industry": "Company industry/sector",
        "target_audience": "Target audience/customer base"
    }
    
    async def main():
        results = await autofill_form(
            "leads",
            "https://releti.no",
            form_fields
        )
        print(results)
    
    asyncio.run(main())