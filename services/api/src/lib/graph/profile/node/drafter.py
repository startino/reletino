from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from src.interfaces.llm import gpt_4o_mini, gpt_o1
from src.interfaces.reddit import get_reddit_instance
from src.lib.graph.profile.tools.subreddit import Subreddit
from src.lib.graph.profile.tools.web_scraper import web_scraper
from src.lib.graph.profile.tools.subreddit import search_relevant_subreddits
from src.lib.graph.profile.state import Context, ProfileState
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.messages import AIMessage
import json

class RecommendationOutput(BaseModel):
    project_name: str = Field(description="The name of the product")
    subreddits: list[Subreddit] = Field(description="The subreddits that are recommended")
    filtering_prompt: str = Field(description="The filtering prompt for the subreddits")
    
class Drafter:
    def __init__(self, context: Context, objective: str):
        self.llm = gpt_o1()
        self.context = context
        self.objective = objective
        
    async def __call__(self, state: ProfileState):
        
        """Main function to analyze product and get recommendations"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
#### **Objective**
Your role is to **automatically configure a project** in Reletino based on the user’s SaaS/business context. This includes:
1. Identifying relevant **subreddits** where potential leads are likely to post.
2. **Drafting a tailored prompt** for the Filter Agent to evaluate posts based on the user’s ideal customer profile.
3. **Ensuring high-quality filtering** by aligning with the user’s business objectives and preferences.
4. **Ensuring the project name is accurate** by combining the objective and the SaaS product name given from context.
---

---

### **Guidelines for Subreddit Selection**
- Look for **communities where the target audience is actively seeking solutions.**  
- Avoid subreddits where posts are dominated by **competitors or non-actionable discussions.**  
- Consider past performance (if available) and suggest only the **most effective** subreddits.

             
### **Guidelines for Project Name**
- The project name should be a combination of the objective and the SaaS product name given from context.
- The project name should be no more than 30 characters.
- The project name should be in sentence case.
---

### **Example Input & Output**

#### **Input:**  
SaaS Name: Hyros
Context: Hyros is an AI-powered ad attribution and optimization platform that helps businesses track and improve their digital advertising performance. Key features include:
- Print tracking technology that captures up to 250% more conversions than standard ad platforms
- AI-powered optimization that improves ad targeting and increases conversions by ~12.5% on average
- Advanced attribution tracking across multiple traffic sources
- Detailed analytics for tracking sales, calls, leads and customer lifetime value
- Forecasting capabilities to predict long-term revenue and ROI
- Integration with major ad platforms like Facebook and Google Ads
- Used by major brands like Tony Robbins, ClickFunnels, and Grant Cardone
- Focused on high-spending advertisers who need maximum accuracy in tracking

#### **Output:**  
**Recommended Subreddits:**  
- r/marketing
- r/EntrepreneurRideAlong
- r/SaaS
- r/AdOps
- r/Entrepreneur
- r/DigitalMarketing
- r/ppc
             
**Filter Agent Prompt:**
- Make sure the prompt is in HTML format.
- Make sure to not add new lines `\n` in the HTML tags.
```
<h2>Objective:</h2>
<p>Find potential clients and leads for Hyros.</p>

<h2>Ideal Customer Profile:</h2>
<ul>
    <li>High-spending advertisers who need maximum accuracy in tracking.</li>
</ul>

<h2>Relevant Posts:</h2>
<ul>
    <li>✅ Posts discussing paid advertising and tracking.</li>
    <li>✅ Posts discussing ad attribution and optimization.</li>
    <li>✅ Posts discussing analytics and reporting.</li>
</ul>

<h2>Irrelevant Posts:</h2>
<ul>
    <li>❌ Posts discussing organic marketing.</li>
    <li>❌ Posts discussing non-advertising related content.</li>
</ul>

<h2>About Hyros</h2>
<p>Hyros is an AI-powered ad attribution and optimization platform that helps businesses track and improve their digital advertising performance. Key features include:</p>
<ul>
    <li>Print tracking technology that captures up to 250% more conversions than standard ad platforms</li>
    <li>AI-powered optimization that improves ad targeting and increases conversions by ~12.5% on average</li>
    <li>Advanced attribution tracking across multiple traffic sources</li>
    <li>Detailed analytics for tracking sales, calls, leads and customer lifetime value</li>
    <li>Forecasting capabilities to predict long-term revenue and ROI</li>
    <li>Integration with major ad platforms like Facebook and Google Ads</li>
</ul>
```
            """),
            ("user", self.context.value)
        ])
        
        chain = prompt | self.llm.bind_tools([RecommendationOutput], tool_choice="any") | JsonOutputToolsParser(return_id=True)
        
        recommendation = (await chain.ainvoke({}))[0]
        
        recommendation["name"] = recommendation["type"]

        results = [
            AIMessage(
                tool_call_id=recommendation["id"],
                content=json.dumps(recommendation["args"]),
                name="drafter",
                tool_calls=[recommendation],
            )
        ]
        
        return {
            "messages": results
        }