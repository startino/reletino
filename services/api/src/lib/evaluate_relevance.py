import textwrap
import os
from dotenv import load_dotenv
from langsmith import traceable

from praw.models import Submission
from langchain_openai import AzureChatOpenAI

from src.interfaces.llm import gpt_4o, gpt_o1, gpt_o3_mini
from src.lib.reddit_profile_analysis import analyze_reddit_user
from src.models import Evaluation

from src.lib.critino import critino_prompt, get_critiques
from src.lib.xml_utils import submission_to_xml

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# AZURE_API_KEY is now loaded directly in the LLM interface functions

REASONING_PROMPT = """
ALWAYS start your reasoning with:
Let's think step by step.
The current situation looking at the submission [...], along with their profile [...].
I am working for a project that is looking for [...].
Perform individual reasoning:
1. Considering the submission, [...], therefore this aspect is [...].
2. Considering the profile, [...], therefore this aspect is [...].
(if any examples from Critino) 3. Considering the critino examples, [...], therefore this aspect is [...].
Use new lines and numbers to separate your thoughts.
"""


@traceable(run_type="chain", name="Evaluate Submission", output_type=Evaluation)
def evaluate_submission(
    submission: Submission,
    project_prompt: str,
    team_name: str,
    project_name: str,
) -> tuple[Evaluation | None, str | None]:
    """
    Evaluates the relevance of a submission using LLMs.

    Parameters:
    - submission: The submission object to be evaluated.
    - project_prompt: The project's prompt to be used for the evaluation. It's the full context of the task.

    Returns:
    - evaluation: The evaluation object containing the relevance score and the reasoning.
    - profile_insights: The profile insights object containing the profile of the author of the submission.
    """

    examples = get_critiques(
        query=submission_to_xml(submission),
        agent_name="evaluator",
        project_name=project_name,
        team_name=team_name,
    )

    def _junior_evaluation() -> Evaluation | None:
        llm = gpt_4o()

        structured_llm = llm.with_structured_output(Evaluation)

        # Try up to 3 times before giving up
        max_retries = 3
        for attempt in range(max_retries):
            try:
                evaluation = structured_llm.invoke(
                    textwrap.dedent(
                        f"""
                {REASONING_PROMPT}
                
                # Context
                You are a super intelligent junior assistant that helps the senior assistant in filtering Reddit posts for the Boss.
                You and the senior assistant have the duty of going through Reddit posts and determining if they are relevant to look into for the Boss.
                You are the first line of defense in filtering out irrelevant posts,
                with the goal of saving time for the senior assistant,
                since there are too many posts that are clearly and blatantly irrelevant.
                It is important to note that because you are a junior assistant,
                you are expected to make mistakes, and because of this and because we do not want to miss any relevant posts,
                you will mark only the most obvious irrelevant posts as irrelevant.
                This means that you should be biased towards marking posts as relevant.

                # Personality and Style
                You are a very intelligent junior assistant, almost like a mathematician. 
                You have a very logical approach to concluding whether a post is relevant to the senior assistant.
                You don't like repeating yourself and redundant text.

                # Project
                Use the context of the project provided to determine if the post is relevant to the project.
                {project_prompt}

                # Post
                This is the post we are evaluating.
                {submission_to_xml(submission)}

                {critino_prompt(examples)}
                """
                    )
                )

                return evaluation  # type: ignore
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e  # Re-raise the exception if all retries failed
                continue

    junior_evaluation = _junior_evaluation()

    if junior_evaluation is None:
        return None, None  # Don't research profiles of irrelevant posts

    if junior_evaluation.is_relevant is False:
        return junior_evaluation, None  # Don't research profiles of irrelevant posts

    # Do further research before making a final decision
    profile_insights = analyze_reddit_user(submission.author.name, project_prompt)

    @traceable(name="Senior Evaluation")
    def _senior_evaluation() -> Evaluation | None:
        llm = gpt_o3_mini()

        structured_llm = llm.with_structured_output(Evaluation)

        # Try up to 3 times before giving up
        max_retries = 3
        for attempt in range(max_retries):
            try:
                senior_evaluation = structured_llm.invoke(
                    textwrap.dedent(
                        f"""
            # Context
            You are a very intelligent senior assistant that filters Reddit posts for your boss.
            You have the duty of going through the Reddit posts and determining if they are relevant to look into for your boss.

            {REASONING_PROMPT}
            
            # Personality and Style
            You are a very intelligent assistant, almost like a mathematician. 
            You have a very logical approach to concluding whether a post is relevant to your boss.
            You don't like repeating yourself and redundant text.

            # Profile Insights
            These are the insights we have about the author of the post based on researching his Reddit profile.
            {profile_insights}

            # Project
            Use the context of the project provided to determine if the post is relevant to the project.
            {project_prompt}

            # Post
            This is the post we are evaluating.
            {submission_to_xml(submission)}

                        {critino_prompt(examples)}
                        """
                    )
                )

                return senior_evaluation  # type: ignore
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e  # Re-raise the exception if all retries failed
                continue

    senior_evaluation = _senior_evaluation()

    return senior_evaluation, profile_insights
