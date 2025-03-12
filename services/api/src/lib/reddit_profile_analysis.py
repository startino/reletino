import asyncio
import os
from typing import Annotated, List
from langsmith import traceable
from pydantic import BaseModel
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.interfaces.llm import gpt_4o, gpt_4o_mini, gpt_o3_mini, openrouter_r1
from src.lib.scrape_reddit_profile import format_profile_for_llm, get_reddit_profile
from src.models.profile import RedditUserProfile
from src.lib.chain_utils import retry_chain_invoke
from langchain_core.runnables import RunnableConfig

class State(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages] = []
    profile: RedditUserProfile
    profile_insights: str | None = None
    project: str

osint_agent_prompt = """
## **OSINT Agent Prompt for Reddit User Profile Analysis**

**Role & Objective**  
You are a specialized OSINT (Open-Source Intelligence) agent tasked with analyzing a Reddit user's profile data to produce concise, **insights** tailored for sales and marketing teams.

### **Instructions**

**Stay Within the Data**  
- Base all insights strictly on the user's posts, comments, and publicly visible profile information.  
- If information is unavailable or inconclusive, explicitly note the limitation.

**Prioritize Structured Analysis**
- Produce your deductions in a step by step manner, showing your exact reasoning and thought process.
- Present your findings in clear, labeled sections corresponding to the framework below.  
- Use bullet points or short paragraphs for clarity.  
- Include direct references or short quotes (if available) to back up each finding.
- Do not return your respond in JSON format.
---

### **Analysis Framework**

**Basic Information**
- Identify the user's full name, age, gender.

**Location and Region**  
- Deduce likely time zone or region based on posting times, language, or explicit mentions of geography.  
- Identify any references to local landmarks, cultural events, or region-specific interests.

**Interests and Hobbies**  
- Identify top subreddits frequented or commonly referenced topics.  
- Pinpoint recurring themes or niche activities.

**Professional Life**  
- Note any discussions related to career goals, industry jargon, or professional affiliations.  
- Identify explicit job titles, sectors, or networking communities.

**Family Dynamics**  
- Look for mentions of immediate or extended family (e.g., spouse, children, or family events).  
- Distinguish personal anecdotes from hypothetical or generalized statements.

**Additional Behavioral Insights**  
- Highlight explicit brand preferences, purchasing behavior, or lifestyle choices.  
- Comment on posting frequency, tone, and engagement style (e.g., helpful, confrontational, informative).  
- Identify any other patterns that could inform user profiling for sales or marketing.
"""

@traceable(name="Generate Insights")
def generate_insights(state: State):
    llm = gpt_4o()
    prompt = ChatPromptTemplate.from_messages([
        ("system", osint_agent_prompt),
        ("system", f"# Profile Data\n{format_profile_for_llm(state.profile)}"),
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({})
    
    return {
        "messages": [response],
    }

@traceable(name="Reflect Insights")
def reflect(state: State):
    llm = gpt_4o()
    prompt = ChatPromptTemplate.from_messages([
        ("system", osint_agent_prompt),
        ("system", "Review the previous analysis and provide critique and additional insights."),
        ("system", f"Last analysis: {state.messages[-1].content}"),
        ("system", f"# Profile Data\n{format_profile_for_llm(state.profile)}"),
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({})
    
    return {
        "messages": [response],
    }

@traceable(name="Summarize Insights")
def summarize(state: State):
    llm = gpt_4o()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Based on the analysis, create a final summary of insights about the user."),
        ("system", f"Last analysis: {str(state.messages[-1].content).replace('{', '{{').replace('}', '}}')}"),
        ("system", """
         You should format your response as HTML, not markdown.
         Your response might look like this:
         <h1>Profile Insights</h1>
         <h2>Basic Information</h2>
         <ul>
            <li><strong>Username:</strong> DesignTechAI</li>
            <li><strong>Karma:</strong> 42 (Comment Karma: 12, Post Karma: 30)</li>
            <li><strong>Account Creation:</strong> March 2023</li>
         </ul>
         """)
    ])
    
    chain = prompt | llm
    
    # Try up to 3 times before giving up
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = chain.invoke({})
            break
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e  # Re-raise the exception if all retries failed
            continue
    
    return {
        "profile_insights": response.content
    }

def create_reflection_agent():
    workflow = StateGraph(State)
    
    workflow.add_node("generate", generate_insights)
    workflow.add_node("reflect", reflect)
    workflow.add_node("summarize", summarize)
    
    workflow.set_entry_point("generate")
    
    workflow.add_edge("generate", "reflect")
    workflow.add_conditional_edges(
        "reflect",
        lambda x: "summarize" if len(x.messages) >= 3 else "generate"
    )
    workflow.add_conditional_edges(
        "generate",
        lambda x: "summarize" if len(x.messages) >= 3 else "reflect"
    )
    workflow.set_finish_point("summarize")
    
    return workflow.compile()

def analyze_reddit_user(username: str, project: str) -> str:
    """
    Use a Reddit user's profile_data that we got with get_reddit_profile to extract insights a Reflection Agent.
    """
    
    insights = ""

    if os.path.exists(f"./.profiles/{username}/profile_insights.txt"):
        with open(f"./.profiles/{username}/profile_insights.txt", "r", encoding="utf-8") as f:
            insights = f.read()
        
    if insights is not "":
        return insights
    
    profile = get_reddit_profile(username)

    if profile is None:
        return "Profile has been suspended or deleted."

    agent = create_reflection_agent()
    initial_state = State(
        messages=[],
        profile=profile,
        profile_insights=None,
        project=project
    )

    config: RunnableConfig = {
        "configurable": {}
    }

    final_state = agent.invoke(initial_state, config=config)

    with open(f"./.profiles/{username}/profile_insights.txt", "w", encoding="utf-8") as f:
        f.write(final_state["profile_insights"]) 
    
    return final_state["profile_insights"]

if __name__ == "__main__":
    
    username = "PastelGripPump"

    insights = analyze_reddit_user(username, "")

    with open(f"./.profiles/{username}/profile_insights.txt", "w", encoding="utf-8") as f:
        f.write(insights)
    
    print(insights)



