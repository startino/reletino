from src.critino import critino, CritinoConfig
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Starting the critino example script")

query = "<title>Idea validation</title><selftext>Kindly do me a favour, give me some tips to validate my product idea. How can I find my product related user.? I need some solid answers.</selftext>"
    
examples = critino(
    query = query,
    agent_name = "main",
    config=CritinoConfig(
        team_name="startino",
        project_name="Software Agency Leads",
        workflow_name="Software Agency Leads",
    )
)

print(examples)