import logging
import os
import requests
from html2text import html2text
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Access environment variables
PUBLIC_CRITINO_API_URL = os.getenv("PUBLIC_CRITINO_API_URL")

class CritinoConfig(BaseModel):
    team_name: str
    project_name: str
    workflow_name: str

def critino(
    query: str,
    agent_name: str,
    config: CritinoConfig,
) -> str:
    examples = "<examples></examples>"
    try:
        config.team_name = html2text(config.team_name)
        config.project_name = html2text(config.project_name)
        config.workflow_name = html2text(config.workflow_name)

        if (
            (config.team_name == "")
            or (config.project_name == "")
            or (config.workflow_name == "")
        ):
            print("team, project, or config name is empty")
            print("team", config.team_name)
            print("project", config.project_name)
            print("config", config.workflow_name)
            return "<examples></examples>"

        team = config.team_name
        project = config.project_name
        workflow_name = config.workflow_name

        body = {
            "query": query,
            "team_name": team.replace(" ", "").replace("\n", ""),
            "project_name": project.replace(" ", "").replace("\n", ""),
            "workflow_name": workflow_name.replace(" ", "").replace("\n", ""),
            "agent_name": agent_name.replace(" ", "").replace("\n", ""),
        }

        url = f"{PUBLIC_CRITINO_API_URL}/critiques/relevant"

        response = requests.post(
            url,
            json=body,
        )

        response_json = response.json()

        examples = response_json.get("examples", "<examples></examples>")
        logging.debug(f"critino: {agent_name}: examples: {examples}")
    except Exception as e:
        logging.error(f"critino: {agent_name}: Error fetching examples: {e}")

    return examples
