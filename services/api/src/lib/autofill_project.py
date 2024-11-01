from typing import Dict, List
from langgraph.graph import StateGraph
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field
import asyncio
from ..interfaces.llm import gpt_4o_mini

class FormField(BaseModel):
    field_id: str = Field(description="HTML field identifier")
    value: str = Field(description="Value to populate the field with")
    confidence: float = Field(description="Confidence score between 0-1")

class WebsiteContent(BaseModel):
    title: str = Field(description="Website title")
    description: str = Field(description="Main website description/content")
    keywords: List[str] = Field(description="Key terms found on the page")

async def scrape_website(url: str) -> str:
    """Scrape website content using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            page = await browser.new_page()
            await page.goto(url)
            
            # Wait for content to load
            await page.wait_for_load_state("networkidle")
            
            # Extract relevant content
            content = WebsiteContent(
                title=await page.title(),
                description=await page.evaluate('document.body.innerText'),
                keywords=await page.evaluate('''
                    Array.from(document.querySelectorAll('meta[name="keywords"]'))
                        .map(el => el.content)
                        .join(',')
                        .split(',')
                ''')
            )
            
            return content.model_dump()
            
        finally:
            await browser.close()

def create_field_node(field_id: str, field_description: str):
    """Create a node for processing a single form field"""
    
    prompt = ChatPromptTemplate.from_template("""
    Based on the website content below, generate an appropriate value for the form field.
    
    Website Content: {website_content}
    
    Field to fill: {field_description}
    
    Generate a value that would be appropriate for this field. Format your response as a FormField object with:
    - field_id: {field_id}
    - value: The generated value
    - confidence: Your confidence in the generated value (0-1)
    
    Response:
    """)
    
    parser = PydanticOutputParser(pydantic_object=FormField)
    
    chain = (
        prompt 
        | gpt_4o_mini(temperature=0.1)
        | parser
    )
    
    return chain

def create_autofill_graph(form_fields: Dict[str, str]) -> StateGraph:
    """
    Create a graph for processing form fields
    
    Args:
        form_fields: Dict mapping field IDs to descriptions
    """
    workflow = StateGraph(name="form_autofill")
    
    # Add nodes for each field
    for field_id, description in form_fields.items():
        node = create_field_node(field_id, description)
        workflow.add_node(field_id, node)
    
    # Connect nodes sequentially
    for i, field_id in enumerate(form_fields.keys()):
        if i > 0:
            prev_field = list(form_fields.keys())[i-1]
            workflow.add_edge(prev_field, field_id)
    
    # Add start edge to first node
    first_field = list(form_fields.keys())[0]
    workflow.set_entry_point(first_field)
    
    return workflow.compile()

async def autofill_form(url: str, form_fields: Dict[str, str]) -> Dict[str, FormField]:
    """
    Main function to autofill a form based on website content
    
    Args:
        url: Website URL to scrape
        form_fields: Dict mapping field IDs to descriptions
        
    Returns:
        Dict mapping field IDs to FormField objects with generated values
    """
    
    # Scrape website
    content = await scrape_website(url)
    
    # Create graph
    graph = create_autofill_graph(form_fields)
    
    # Add website content to inputs
    inputs = {
        field_id: {"website_content": content, "field_id": field_id, "field_description": desc}
        for field_id, desc in form_fields.items()
    }
    
    # Execute graph
    results = await graph.ainvoke(inputs)
    
    return results

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
            "https://example-saas.com",
            form_fields
        )
        print(results)
    
    asyncio.run(main())