import json
from typing import Dict, List, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnablePassthrough
from bs4 import BeautifulSoup
import aiohttp
from pydantic import BaseModel, Field
import asyncio
from src.interfaces.llm import gpt_4o_mini, gpt_o1
import logging
from langchain.tools import Tool
from langchain.tools.tavily_search.tool import TavilySearchResults
from langgraph.prebuilt import ToolNode
from sse_starlette import ServerSentEvent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FormField(BaseModel):
    label: str = Field(description="Label of the field")
    description: str = Field(description="Description of the field")
    value: str = Field(description="Value to populate the field with", default="")

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
    last_updated_field: FormField | None = None
    current_action: Action | None = None
    research_output: str | None = None


async def autofill_form(use_case: Literal["leads", "competition_research", "other"], url: str, fields: list[FormField]):
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
                    llm = gpt_o1().with_structured_output(ProcessedWebsite)
                    
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
                    
                    return processed_website # type: ignore
                    
            except Exception as e:
                logger.error(f"Error processing website: {e}", exc_info=True)
                raise
    
    async def field_autocompleter(state: State):

        if not state.processed_website:
            logger.debug("No processed website, skipping field autocompleter")
            return
        
        if not state.current_action:
            logger.debug("No current action, skipping field autocompleter")
            return

        logger.debug(f"Processing field: {state.current_action.field_label}")
        
        # Create prompt with required variables
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an AI assistant that fills form fields based on website content for the use case of: {state.use_case}.
            
            ### WEBSITE CONTENT ###
            Business Name: {state.processed_website.business_name}
            Summary: {state.processed_website.summary}
            
            ### FORM FIELD ###
            Fill this form field:
            Label: {state.current_action.field_label}
            Description: {next((field.description for field in state.form if field.label == state.current_action.field_label), "No description found")}
            """
        ),
        ])
        
        # Create structured agent with tools
        llm = gpt_4o_mini()
        agent = prompt | llm.with_structured_output(FormField)
        
        result = await agent.ainvoke({})
        
        # Convert result to FormField
        completed_field = FormField(
            label=state.current_action.field_label,
            description=next((field.description for field in state.form if field.label == state.current_action.field_label), "No description found"),
            value=result.value
        )
        
        # Update form with new field value
        updated_form = [
            completed_field if field.label == state.current_action.field_label else field
            for field in state.form
        ]
        
        return {"form": updated_form, "current_action": None, "last_updated_field": completed_field}

    async def process_next_field(state: State):
        """Process next empty field in sequence"""
        empty_fields = [field for field in state.form if field.value == ""]
        if not empty_fields:
            return {"current_action": Action(reasoning="All fields complete", action="finish", field_label=None)}
        
        next_field = empty_fields[0]
        return {"current_action": Action(
            reasoning=f"Processing field {next_field.label}",
            action="fill_field",
            field_label=next_field.label
        )}
        
    async def research_graph(state: State):
        """Research using Tavily search"""
        
        tavily_tool = TavilySearchResults(max_results=3)
        tools = [tavily_tool]
        
        prompt = f"""
        You are an expert researcher.
        
        You are helping a business owner fill out a form for the use case of: {state.use_case}.
        Specifically, you are helping research before your teammate fills out the form.
        
        You will usually research to find out more about the business like their competitors and target audience.
        
        Use Tavily to research.
        If you have nothing left to research, you should return a report of your
        research while being sure to not using Tavily in this final step.
        
        Start the research process with researching competitors.
        Then research to find out more about the target audience.
        
        ### EXAMPLES ###
        For the target audience, search things like "who uses [type of product]"
        For competitors, search things like "best [type of product] for [target audience]"
        
        ### WEBSITE CONTENT ###
        Business Name: {state.processed_website.business_name}
        Summary: {state.processed_website.summary}
        """
        
        graph = create_react_agent(gpt_4o_mini(), tools=tools, state_modifier=prompt)

        for state in graph.stream({"messages": [("user", "Start researching")]}, stream_mode="values"):
            message = state["messages"][-1]
            if not isinstance(message, tuple):
                last_message = message.content
        
        return {"research_output": last_message}

    # Create graph
    workflow = StateGraph(State)
    
    # Replace supervisor with process_next_field
    workflow.add_node("research", research_graph)
    workflow.add_node("process_next_field", process_next_field)
    workflow.add_node("field_autocompleter", field_autocompleter)
    
    def routing_function(state: State) -> Literal["fill_field", "finish"]:  
        return END if state.current_action.action == "finish" else "try_again"
    
    workflow.add_conditional_edges(
        "process_next_field",
        routing_function,
        {
            "try_again": "field_autocompleter",
            END: END
        }
    )
    
    workflow.add_edge("field_autocompleter", "process_next_field")
    workflow.set_entry_point("research")

    # Add website content to inputs
    starting_state: State = State(
        use_case=use_case,
        url=url,
        form=fields,
        processed_website= await website_processing()
    )
    
    graph = workflow.compile()
    
    # Execute graph
    async for state in graph.astream(starting_state, stream_mode="values"):
        # The order of the if statements is important
        # The order of the graph is: process website -> research -> field_autocompleter loop
        if state.last_updated_field:
            # yield the most recent field
            yield state.last_updated_field
        elif state.research_output:
            yield ServerSentEvent(
                data=json.dumps(state.research_output),
                event="research_finished",
            )
        elif state.processed_website:
            yield ServerSentEvent(
                data=json.dumps(state.processed_website.model_dump()),
                event="website_processing_finished",
            )


# Example usage:
if __name__ == "__main__":
    form_fields = [
        FormField(label="business name", description="Company name, company should be a product or service"),
        FormField(label="about", description="A 2 - 4 sentence description of the product or service"),
        FormField(label="subreddits", description="Subreddits to post to, should be relevant to the product or service"),
        FormField(label="ideal customer profile", description="Target audience/customer base, should be relevant to the product or service"),
        FormField(label="competitors", description="Competition, what are the main competitors?"),
        FormField(label="unique selling points", description="What makes you different from the competition?"),
    ]
    
    async def main():
        results = await autofill_form(
            "leads",
            "https://www.tryfriendli.com/",
            fields=form_fields
        )
        print(results)
    
    asyncio.run(main())