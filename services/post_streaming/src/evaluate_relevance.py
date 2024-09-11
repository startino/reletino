import time
from typing import List
import os
from dotenv import load_dotenv

from gptrim import trim
from praw.models import Submission
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_community.callbacks import get_openai_callback

from src.models import Evaluation, Evaluation, FilterOutput, FilterQuestion
from src.prompts import calculate_relevance_prompt, context as company_context, purpose
from src.filter_with_questions import filter_with_questions

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

    # Trim the submission content for cost savings
    selftext = trim(submission.selftext)

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


def evaluate_submission(submission: Submission, filter_questions: list[FilterQuestion] | None = None ) -> Evaluation:
    """
    Determines the relevance of a submission using GPT-3.5-turbo,
    optionally escalating to GPT-4-turbo for higher accuracy.

    Parameters:
    - submission: The submission object to be evaluated.

    Returns:
    - is_relevant (bool): Final relevance decision based on the used model(s).
    - total_cost (float): The total cost incurred from relevance calculations.
    """

    if filter_questions != None:
        questions = [
            FilterQuestion(
                question="Is the author himself an IT person? is/was he a programmer? is/was he a software developer?",
                reject_on=True,
            ),
            FilterQuestion(
                question="Is the author currently engaged in job searching activities and promoting their technical expertise?",
                reject_on=True,
            ),
            FilterQuestion(
                question="Is the author starting a non digital business? Like a bakery, garden business, salon, etc.",
                reject_on=True,
            ),
        ]

        evaluation: Evaluation = filter_with_questions(submission, questions)
        
        if not evaluation.is_relevant:
            print("Filtered out submission")
            print("Source: ", evaluation.source)
            print("Title: ", submission.title)
            print("Selftext: ", submission.selftext)
            print("\n")
            return evaluation
        
    llm = AzureChatOpenAI(
        api_key=AZURE_API_KEY,
        deployment_name="gpt-4o",
        model="gpt-4o",
        azure_endpoint="https://startino.openai.azure.com/",
        api_version="2024-02-01",
        max_retries=20,
    )

    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=Evaluation)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser

    for _ in range(3):
        try:
            with get_openai_callback() as cb:
                evaluation: Evaluation = chain.invoke(
                    {
                        "query": f"{calculate_relevance_prompt} \n\n #POST CONTENT:\n ```{submission.title}\n{submission.selftext}```"
                    }
                )
        except Exception as e:
            print(f"An error occurred while evaluating relevance: {e}")
            time.sleep(2)

    return evaluation