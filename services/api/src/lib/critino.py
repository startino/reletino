import logging
import os
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.messages import BaseMessage
import requests
from html2text import html2text
from dotenv import load_dotenv

from src.lib import xml_utils

load_dotenv()

# Access environment variables
PUBLIC_CRITINO_API_URL = os.getenv("PUBLIC_CRITINO_API_URL")


def normalize(text: str) -> str:
    return html2text(text).replace("\n", "").replace(" ", "").replace("\\", "").lower()


def format_example_string(critiques: list[dict]) -> str:
    example_prompt = PromptTemplate.from_template(
        "<example><context>{context}</context><query>{query}</query><output>{optimal}</output></example>"
    )

    few_shot = FewShotPromptTemplate(
        examples=critiques,
        example_prompt=example_prompt,
        example_separator="",
        prefix="<examples>",
        suffix="</examples>",
    ).format()

    return xml_utils.trim_xml(few_shot)


def critino(
    query: str,
    agent_name: str,
    project_name: str,
    environment_name: str,
) -> str:
    logging.info(f"critino: {agent_name}")
    examples = "<examples></examples>"
    try:
        logging.info(f"critino: {agent_name}: try")

        params = {
            "team_name": "startino",
            "environment_name": "reletino/" + environment_name + "/" + project_name,
            "workflow_name": project_name,
            "agent_name": "main",
            "query": query,
            "k": 5,
        }

        logging.info(f"critino: {agent_name}: params: {params}")

        url = f"{PUBLIC_CRITINO_API_URL}/critiques"

        x_critino_key = os.getenv("PUBLIC_CRITINO_API_KEY")
        if not x_critino_key:
            logging.error("critino: x_critino_key is empty")
            return "<examples></examples>"

        response = requests.get(
            url,
            params=params,
            headers={"X-Critino-Key": x_critino_key},
            timeout=10,
        )
        response_json = response.json()

        examples = format_example_string(response_json.get("data", []))
        logging.info(f"critino: {agent_name}: examples: {examples}")
    except requests.exceptions.Timeout:
        logging.error(f"critino: {agent_name}: Request timed out")
    except Exception as e:
        logging.error(f"critino: {agent_name}: Error fetching examples: {e}")

    return examples
