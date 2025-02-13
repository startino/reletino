import os

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import SecretStr
from langchain_community.chat_models import ChatPerplexity


def openrouter_r1(temperature: float = 0.5) -> ChatOpenAI:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    assert (
        OPENROUTER_API_KEY is not None
    ), "Environment variable 'OPENROUTER_API_KEY' is not set"

    return ChatOpenAI(
        api_key=SecretStr(OPENROUTER_API_KEY),
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-r1",
        temperature=temperature,
        max_retries=20,
        default_headers={
            "HTTP-Referer": "https://releti.no",
            "X-Title": "Reletino"
        }
    )

def gpt_o3_mini(temperature: float = 0.5) -> AzureChatOpenAI:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    assert (
        AZURE_OPENAI_API_KEY is not None
    ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"
    
    return AzureChatOpenAI(
        api_key=SecretStr(AZURE_OPENAI_API_KEY),
        azure_deployment="o3-mini",
        model="o3-mini",
        azure_endpoint="https://startino.openai.azure.com/",
        api_version="2024-12-01-preview",
        max_retries=20,
    )

# def gpt_o1_mini(temperature: float = 0.5) -> AzureChatOpenAI:
#     AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
#     assert (
#         AZURE_OPENAI_API_KEY is not None
#     ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"
    
#     return AzureChatOpenAI(
#         api_key=SecretStr(AZURE_OPENAI_API_KEY),
#         azure_deployment="o1-mini",
#         model="o1-mini",
#         azure_endpoint="https://startino.openai.azure.com/",
#         api_version="2024-10-01-preview",
#         temperature=0.0
#     )

def gpt_o1(temperature: float = 0.5) -> AzureChatOpenAI:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    assert (
        AZURE_OPENAI_API_KEY is not None
    ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"

    return AzureChatOpenAI(
        api_key=SecretStr(AZURE_OPENAI_API_KEY),
        azure_deployment="o1",
        model="o1",
        azure_endpoint="https://startino.openai.azure.com/",
        api_version="2024-12-01-preview",
        max_retries=20,
    )

def gpt_4o_mini(temperature: float = 0.5) -> AzureChatOpenAI:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    assert (
        AZURE_OPENAI_API_KEY is not None
    ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"
    
    AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    assert (
        AZURE_OPENAI_API_ENDPOINT is not None
    ), "Environment variable 'AZURE_OPENAI_API_ENDPOINT' is not set"
    
    return AzureChatOpenAI(
        streaming=True,
        azure_deployment="gpt-4o-mini",
        temperature=temperature,
        api_key=SecretStr(AZURE_OPENAI_API_KEY),
        azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
        model="gpt-4o-mini",
        api_version="2024-06-01",
        max_retries=20,
    )

def gpt_4o(temperature: float = 0.5) -> AzureChatOpenAI:
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    assert (
        AZURE_OPENAI_API_KEY is not None
    ), "Environment variable 'AZURE_OPENAI_API_KEY' is not set"

    AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    assert (
        AZURE_OPENAI_API_ENDPOINT is not None
    ), "Environment variable 'AZURE_OPENAI_API_ENDPOINT' is not set"

    return AzureChatOpenAI(
        streaming=True,
        azure_deployment="gpt-4o",
        temperature=temperature,
        api_key=SecretStr(AZURE_OPENAI_API_KEY),
        azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
        model="gpt-4o",
        api_version="2024-06-01",
        max_retries=20,
    )


def gpt_4o_mini_not_azure(temperature: float = 0.5) -> ChatOpenAI:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    assert (
        OPENAI_API_KEY is not None
    ), "Environment variable 'OPENAI_API_KEY' is not set"

    return ChatOpenAI(
        streaming=True,
        model="gpt-4o-mini",
        temperature=temperature,
        api_key=SecretStr(OPENAI_API_KEY),
    )


def gpt_4o_not_azure(temperature: float = 0.5) -> ChatOpenAI:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    assert (
        OPENAI_API_KEY is not None
    ), "Environment variable 'OPENAI_API_KEY' is not set"

    return ChatOpenAI(
        model="gpt-4o",
        temperature=temperature,
        api_key=SecretStr(OPENAI_API_KEY),
    )


def perplexity(temperature: float = 0.7) -> ChatPerplexity:
    """
    Models: https://docs.perplexity.ai/guides/model-cards
    """
    PERPLEXITY_AI_KEY = os.getenv("PERPLEXITY_AI_KEY")

    assert (
        PERPLEXITY_AI_KEY is not None
    ), "Environment variable 'PERPLEXITY_AI_KEY' is not set"

    return ChatPerplexity(
        temperature=temperature,
        model="llama-3.1-sonar-small-128k-online",
        timeout=15,
        api_key=PERPLEXITY_AI_KEY,
    )
