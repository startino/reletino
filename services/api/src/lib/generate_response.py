import textwrap
from dotenv import load_dotenv
from src.lib.critino import critino_prompt, get_critiques
from src.interfaces.db import client
from src.interfaces.llm import gpt_o1, gpt_4o, gpt_o3_mini, openrouter_r1, gemini_flash_2
from src.lib.reddit_profile_analysis import analyze_reddit_user
from src.lib.xml_utils import submission_to_xml
from src.models.simple_submission import SimpleSubmission
from src.models.cot_response import CotResponse
import json

load_dotenv()
    
def generate_response(submission: SimpleSubmission, team_name: str, project_id: str, is_dm: bool, feedback: str) -> str:
    supabase = client()
    if is_dm:
        project = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    else:
        project = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    
    if not project.data:
        raise Exception(f"Project not found: {project_id}")
    
    project_name = project.data["title"]
    style_prompt = project.data["dm_style_prompt"] if is_dm else project.data["comment_style_prompt"]
    project_prompt = project.data["prompt"]

    llm = gemini_flash_2()

    examples = get_critiques(
        team_name=team_name,
        project_name=project_name,
        agent_name="dm-generator" if is_dm else "comment-generator",
        query=submission_to_xml(submission),
        )
    
    profile_insights = analyze_reddit_user(submission.author_name, project_prompt)

    feedback_section = f"""
    ### Feedback ###
    Please incorporate this feedback into your response:
    {feedback}
    
    ####################
    """

    structured_llm = llm.with_structured_output(CotResponse)
    response = structured_llm.invoke(
        textwrap.dedent(
            f"""
            Your job is to:
            {"write a DM" if is_dm else "write a comment"}
            for a Reddit post.
            
            ####################
            
            ### Style ###
            {style_prompt}
            
            ####################
            
            ### Post ###
            {submission_to_xml(submission)}

            ####################
            
            ### Profile Insights ###
            These are the insights we have about the author of the post based on researching his Reddit profile.
            {profile_insights}
            
            ####################
            {feedback_section}
            ### Examples ###
            {critino_prompt(examples)}

            First, think through your approach step by step, analyzing the post, profile insights, and how to best craft your response.
            Then provide your final response in JSON format with the following structure:
            {{
                "chain_of_thought": "Your step by step reasoning",
                "response": "Your final response"
            }}
            """
        ))
    
    # If the response is a string, try to parse it as JSON
    if isinstance(response, str):
        try:
            response_dict = json.loads(response)
            return response_dict["response"]
        except json.JSONDecodeError:
            # If JSON parsing fails, return the response as is
            return response
    elif isinstance(response, dict):
        return response.get("response", str(response))
    
    return response.response