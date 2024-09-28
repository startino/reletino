import time
from typing import List
import os
from dotenv import load_dotenv

from praw.models import Submission
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_community.callbacks import get_openai_callback

from src.models import Evaluation
from src.prompts import calculate_relevance_prompt, context as company_context, purpose
from src.filter_with_questions import filter_with_questions

from src.critino import critino, CritinoConfig

# Load Enviornment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")


def summarize_submission(submission: Submission) -> Submission:
    """
    Summarizes the content of a submission using LLMs.
    Uses a soft summarizing strength and only summarises each paragraph.
    It aims to reduce the token count of the submission content by 50%.

    Parameters:
    - submission (Submission): The submission object to be summarized.

    Returns:
    - The submission object with the selftext replaced with a shorter version (the summary).
    """
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4-turbo",
        temperature=0,
    )

    selftext = submission.selftext

    # Short submissions are not summarized
    if llm.get_num_tokens(selftext) < 150:
        return submission

    template = f"""
    # Welcome Summary Writer!
    Your job is to help a Virtual Assistant in filtering Reddit posts.
    You'll help by summarizing the content of a Reddit post to remove any useless parts.

    # Guidelines
    - Extract information from each sentence and include it in the summary.
    - Use bullet points to list the main points.
    - DO NOT remove any crucial information.
    - IF PRESENT, you must include information about the author such as his profession(or student) and if he knows how to code.
    - DO NOT make up any information that was not present in the original text.
    - Commendations and encouragements should be removed.
    # Body Text To Summarize
    ```
    {selftext}
    ```


    # Here is more information for context

    {company_context}

    ## Purpose of this process
    {purpose}

    """
    
    summary = llm.invoke(template)
    summarized_selftext = summary.content

    # Calculate token reduction
    pre_token_count = llm.get_num_tokens(selftext)
    post_token_count = llm.get_num_tokens(str(summarized_selftext))
    reduction = (pre_token_count - post_token_count) / pre_token_count * 100

    # Print the token reduction
    print(f"Token reduction : {reduction:.3f}%")

    # Update the submission object with the summarized content
    submission.selftext = summarized_selftext

    return submission


def evaluate_submission(
    submission: Submission,
    project_prompt: str,
    environment_name: str,
    workflow_name: str,
    project_name: str,
    ) -> Evaluation | None:
    """
    Evaluates the relevance of a submission using LLMs.

    Parameters:
    - submission: The submission object to be evaluated.
    - project_prompt: The project's prompt to be used for the evaluation. It's the full context of the task.

    Returns:
    - evaluation: The evaluation object containing the relevance score and the reasoning.
    """
 
    llm = AzureChatOpenAI(
        api_key=AZURE_API_KEY,
        deployment_name="gpt-4o",
        model="gpt-4o",
        azure_endpoint="https://startino.openai.azure.com/",
        api_version="2024-02-01",
        max_retries=20,
    )

    parser = PydanticOutputParser(pydantic_object=Evaluation)

    prompt = PromptTemplate(
        template="<format-instructions>{format_instructions}</format-instructions><universal-prompt>{universal_prompt}</universal-prompt> <project-prompt>{project_prompt}</project-prompt><query>{query}</query> {examples}",
        input_variables=["query", "examples", "project_prompt", "universal_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    
    total_cost = 0
    
    evaluation: Evaluation | None = None
    
    query = f"""
    <post>
        <title>
            {submission.title}
        </title>
        <selftext>
            {submission.selftext}
        </selftext>
    </post>
    """
        
    examples = critino(
        query = query,
        agent_name = "main",
        config=CritinoConfig(
            team_name=environment_name,
            project_name=project_name,
            workflow_name=workflow_name,
        )
    )
    
    universal_prompt = """
<context>
    Imagine you are a super talented virtual assistant.
    You have the duty of going through Reddit posts and determining if they are relevant to look into for your boss.
</context>
<personality-and-style>
	You are a very intelligent assistant, almost like a mathematician. 
	You have a very logical approach to concluding whether a post is relevant to your boss.
	You don't like repeating yourself and redundant text.
</personality-and-style>
    """

    for _ in range(3):
        try:
            with get_openai_callback() as cb:
                evaluation = chain.invoke(
                    {
                        universal_prompt: universal_prompt,
                        "project_prompt": project_prompt,
                        "query": query,
                        "examples": examples,
                    }
                )
                total_cost += cb.total_cost
        except Exception as e:
            print(f"An error occurred while evaluating relevance: {e}")
            time.sleep(5)
            
    return evaluation
