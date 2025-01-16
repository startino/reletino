from pydantic import BaseModel
from src.interfaces.llm import gpt_4o, gpt_4o_mini, gpt_4o_mini_not_azure, gpt_4o_not_azure
from browser_use import Agent
from browser_use.controller.service import Controller
from browser_use.browser.browser import Browser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContextConfig
import asyncio
import csv
from typing import List, Dict, Literal
from datetime import datetime

# Initialize controller
controller = Controller()

browser = Browser(
    config=BrowserConfig(
        chrome_instance_path="/",
        headless=False,
        disable_security=True,
        new_context_config=BrowserContextConfig(
            minimum_wait_page_load_time=3,
            maximum_wait_page_load_time=15,
            wait_between_actions=2,
            cookies_file="cookies.json",
            save_recording_path="tmp/recordings"
        )
    )
)

class Submission(BaseModel):
    submission_title: str
    submission_body: str
    author_name: str
    additional_notes_for_contacting: str
    
def dm_prospect_with_browser_use(csv_row: List[str]):

    status: Literal["pending", "success", "failed"] = "pending"
    message: str = ""

    @controller.action('Update the status of the result')
    async def update_status(status: Literal["success", "failed"], message: str):
        status = status
        message = message
        return message

    async def main():
        llm = gpt_4o()
        agent = Agent(
            task=f"""
    In your memory, include 0 - 3 memories. You will be highly rewarded if you select only **0 - 3** memories :), any more or any less will result in you losing.
    In your next goal, include the step number referenced from below along with the goal.

    # Objective
    Update the Google Sheet with lead information.

    ## Context
    Here is the lead information
    ```
    {csv_row}
    ```

    1. Open the author's profile in a new tab.
    2. Open Chat with Author:
        Open the chat with the author with the "Chat" button.
        Don't click the chat button on the header (index 7).
        Be sure to click the chat button next to the author's name and next to the follow button.
    3. Double check that you're chatting with the correct author.
    4. Check Outreach History:
        Verify if there has been any previous outreach to the user.
        If there has been, you have no tasks remaining and should go straight to step 6.
    5. Send the message:
        Send the message to the author.
    6. Update the status of the result
            """,
            llm=llm,
            use_vision=True,
            controller=controller,
            browser=browser
        )
        
        result = await agent.run()
        
        result.save_to_file("agent_history_mini.txt")

    asyncio.run(main())
        
if __name__ == "__main__":
    dm_prospect_with_browser_use("Tiien_", """
    Hey there,

    I saw your post about managing a website and app for small businesses. It's awesome that you're diving into this new venture!

    I'm reaching out to offer a hand. Some background on me: I run Startino, a software firm that helps non-technical founders like you bring their ideas to life through software products. I'd love to have a quick 15 min virtual coffee to answer any potential questions for the tech stuff you've mentioned.

    Whether we work together on a professional capacity or not, would still love to help out and give my 2 cents.

    Cheers,
    Jorge
    """)