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

from src.models import FilterOutput, FilterQuestion, Evaluation

# uses gpt-3.5-turbo to filter out irrelevant posts by using simple yes no questions
def filter_with_questions(
    submission: Submission, questions: list[FilterQuestion]
) -> Evaluation:
    """
    Filters out irrelevant posts by asking simple yes/no questions to the LLM.
    The questions are generated using GPT-3.5-turbo.

    If any one of the questions is answered with a NO, the submission is considered irrelevant.

    Parameters:
    - submission (Submission): The submission object to be filtered.
    - questions (list[str]): A list of yes-no questions to be asked to the LLM.
    YES answers mean the submission is kept (kept).
    NO answers mean the submission is discarded (irrelevant).

    Returns:
    - A boolean indicating whether the submission is relevant.
    (True = relevant, False = irrelevant)
    - The question that caused the submission to be filtered out.
    """

    cost = 0

    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",
        temperature=0,
    )
    parser = PydanticOutputParser(pydantic_object=FilterOutput)

    template = """
    You are a helpful assistant that helps to filter posts.
    You will read a Reddit post, and then answer a yes-no question based on the 
    post's content and provide the source.

    The term "OP" refers to Original Poster, the person who made the post, also
    known as the author.

    {format_instructions}
    
    # Question
    {question}

    # Post
    Title: {title}
    Content: {selftext}
    """

    for question in questions:

        prompt = PromptTemplate(
            template=template,
            input_variables=["question", "title", "selftext"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm | parser

        # Error checking since gpt-3.5 sucks at json formatting lol
        for i in range(10):
            try:
                with get_openai_callback() as cb:
                    result = chain.invoke(
                        {
                            "question": question.question,
                            "title": submission.title,
                            "selftext": submission.selftext,
                        }
                    )
                    # TODO: Do some cost analysis and saving (for long term insights)
                    cost += cb.total_cost
                break
            except Exception as e:
                print(f"An error occurred while filtering using questions: {e}")
                time.sleep(1)  # Wait for 10 seconds before trying again
                if i == 10:
                    return Evaluation(is_relevant=False, reason="Error occurred while filtering with questions")

        filter_output = FilterOutput.parse_obj(result)

        if question.reject_on == filter_output.answer:
            # Submission is irrelevant
              return Evaluation(is_relevant=False, reason=f"Filtered with question: {filter_output.source}")
        else:
            # Submission is relevant
            return Evaluation(is_relevant=True, reason=f"Filtered with question: {filter_output.source}")

  