import json
import logging
import os
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.messages import BaseMessage
import requests
from html2text import html2text
from dotenv import load_dotenv
from fastapi import HTTPException

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

def critino_prompt(examples: str) -> str:
    return f"""
    # Auto generated message sent to you by Critino so you can refer to the examples to emulate their optimal answers
    <critino>
    {examples}

    > NOTE: Make sure you very strongly consider and emulate the optimal answers along with the length, consiseness, etc from them accurately.
    > They represent previous generations of responses that were absolutely amazing!
    > This does not mean that you should copy paste the answers from them, but rather emulate them as closely as possible.
    > Make sure to seriously consider them in your chain of thoughts and use them as a reference to answer the question.
    > Make sure to reason about how the answer is derived and how it fits into the larger context of the conversation.
    > Keep in mind! No matter how similar the conversation may seem to the examples, none of the facts or information in the examples about who you are speaking to are are related to your current conversation, if they are the same it's pure happenstance.
    </critino>
    """.strip()
    
def get_critiques(
    query: str,
    agent_name: str,
    project_name: str,
    team_name: str,
    context: str = "",
    timeout: int = 300,
) -> str:
    logging.info(f"critino: {agent_name}")
    examples = {}
    try:
        logging.info(f"critino: {agent_name}: query: {query}")

        params = {
            "team_name": "startino",
            "environment_name": "reletino/" + team_name + "/" + project_name + "/" + agent_name,
            "query": query,
            "k": 3,
            "similarity_key": "situation",
        }

        logging.info(f"critino: {agent_name}: params: {params}")

        url = f"{PUBLIC_CRITINO_API_URL}/critiques"

        x_critino_key = os.getenv("PUBLIC_CRITINO_API_KEY")
        if not x_critino_key:
            raise HTTPException(
                status_code=500, detail="PUBLIC_CRITINO_API_KEY is empty"
            )

        x_openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not x_openrouter_api_key:
            raise HTTPException(
                status_code=500, detail="OPENROUTER_API_KEY is empty"
            )

        response = requests.get(
            url,
            params=params,
            headers={
                "X-Critino-Key": x_critino_key,
                "X-OpenRouter-API-Key": x_openrouter_api_key,
            },
            timeout=timeout,
        )
        response_json = response.json()

        examples = response_json.get("data", {})
        logging.info(f"critino: {agent_name}: examples: {examples}")
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504, detail=f"Request timed out after {timeout} seconds"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching examples: {e}")

    if not examples:
        logging.info(f"critino: {agent_name}: No critiques were fetched")

    return json.dumps(examples, indent=2).replace("{", "{{").replace("}", "}}")
