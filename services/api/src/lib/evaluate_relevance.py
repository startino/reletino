import textwrap
import time
import os
from dotenv import load_dotenv
from langsmith import traceable

from praw.models import Submission
from langchain_openai import AzureChatOpenAI
from langchain_community.callbacks import get_openai_callback

from src.models import Evaluation, project
from src.prompts import context as company_context, purpose

from src.lib.critino import critino

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


@traceable(run_type="chain", name="Evaluate Submission", output_type=Evaluation)
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

    total_cost = 0

    post_query = f"""
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
        query=post_query,
        agent_name="main",
        project_name=project_name,
        environment_name=environment_name,
    )

    @traceable
    def junior_evaluation() -> Evaluation:
        llm = AzureChatOpenAI(
            api_key=AZURE_API_KEY,
            deployment_name="gpt-4o-mini",
            model="gpt-4o-mini",
            azure_endpoint="https://startino.openai.azure.com/",
            api_version="2024-02-01",
            max_retries=20,
        )

        structured_llm = llm.with_structured_output(Evaluation)

        junior_evaluation: Evaluation = structured_llm.invoke(
            textwrap.dedent(
                f"""
            <format-instructions>
                {{
                    "reasoning": "... ...",
                    "is_relevant": "..."
                }}
            </format-instructions>
            <context>
                You are a super intelligent junior assistant that helps the senior assistant in filtering Reddit posts for the Boss.
                You and the senior assistant have the duty of going through Reddit posts and determining if they are relevant to look into for the Boss.
                You are the first line of defense in filtering out irrelevant posts,
                with the goal of saving time for the senior assistant,
                since there are too many posts that are clearly and blatantly irrelevant.
                It is important to note that because you are a junior assistant,
                you are expected to make mistakes, and because of this and because we do not want to miss any relevant posts,
                you will mark only the most obvious irrelevant posts as irrelevant.
                This means that you should be biased towards marking posts as relevant.
            </context>
            <personality-and-style>
                You are a very intelligent junior assistant, almost like a mathematician. 
                You have a very logical approach to concluding whether a post is relevant to the senior assistant.
                You don't like repeating yourself and redundant text.
            </personality-and-style>
            <project-instructions>
                {project_prompt}
            </project-instructions>
            {post_query}
            {examples}
            """
            )
        )

        return junior_evaluation

    junior_evaluation = junior_evaluation()

    if junior_evaluation.is_relevant is False:
        return junior_evaluation

    @traceable
    def senior_evaluation() -> Evaluation:
        llm = AzureChatOpenAI(
            api_key=AZURE_API_KEY,
            deployment_name="gpt-4o",
            model="gpt-4o",
            azure_endpoint="https://startino.openai.azure.com/",
            api_version="2024-02-01",
            max_retries=20,
        )

        structured_llm = llm.with_structured_output(Evaluation)

        senior_evaluation: Evaluation = structured_llm.invoke(
            textwrap.dedent(
                f"""
            <format-instructions>
                {{
                    "reasoning": "... ...",
                    "is_relevant": "..."
                }}
            </format-instructions>
            <context>
                You are a very intelligent senior assistant that filters Reddit posts for your boss.
                You have the duty of going through the Reddit posts and determining if they are relevant to look into for your boss.
            </context>
            <personality-and-style>
                You are a very intelligent assistant, almost like a mathematician. 
                You have a very logical approach to concluding whether a post is relevant to your boss.
                You don't like repeating yourself and redundant text.
            </personality-and-style>
            <project>
                {project_prompt}
            </project>
            {post_query}
            {examples}
            """
            )
        )
        return senior_evaluation

    senior_evaluation = senior_evaluation()

    return senior_evaluation
