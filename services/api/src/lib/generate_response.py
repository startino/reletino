import textwrap
from dotenv import load_dotenv
from src.lib.critino import get_critiques
from src.interfaces.db import client
from src.interfaces.llm import gpt_4o
from src.lib.reddit_profile_analysis import analyze_reddit_user
from src.lib.xml_utils import submission_to_xml
from src.models.simple_submission import SimpleSubmission
load_dotenv()

def generate_response(submission: SimpleSubmission, team_name: str, project_id: str, is_dm: bool) -> str:
    supabase = client()
    if is_dm:
        project = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    else:
        project = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    
    if not project.data:
        raise Exception(f"Project not found: {project_id}")
    
    project_name = project.data["title"]
    style_prompt = project.data["dm_style_prompt"] if is_dm else project.data["comment_style_prompt"]

    llm = gpt_4o()

    examples = get_critiques(
        team_name=team_name,
        project_name=project_name,
        agent_name="dm-generator" if is_dm else "comment-generator",
        query=submission_to_xml(submission),
        )
    
    profile_insights = analyze_reddit_user(submission.author_name)

    response = llm.invoke(
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
            
            Title: {submission.title}
            
            Selftext: {submission.selftext}

            ####################
            
            ### Profile Insights ###
            These are the insights we have about the author of the post based on researching his Reddit profile.
            {profile_insights}
            
            ####################
            
            ### Examples ###
            These are semantically similar examples of comments/dms that we have evaluated in the past and has been verified to be a good comment/dm by a human.
            The `query` is the post and the `optimal` is the optimal response given by a human.
            {examples}
            """
        )
    )
    return response.content