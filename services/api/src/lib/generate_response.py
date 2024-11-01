from praw.models import Submission
import textwrap
from dotenv import load_dotenv
from src.lib.critino import critino
from src.interfaces.db import client
from src.interfaces.llm import gpt_4o

load_dotenv()

def generate_response(submission: Submission, project_id: str, is_dm: bool) -> str:
    supabase = client()
    if is_dm:
        style_prompt = supabase.table("projects").select("dm_style_prompt").eq("id", project_id).single().execute()
    else:
        style_prompt = supabase.table("projects").select("comment_style_prompt").eq("id", project_id).single().execute()
    
    if not style_prompt.data:
        raise Exception(f"Project not found: {project_id}")
    
    style_prompt = style_prompt.data[0]

    llm = gpt_4o()

    response = llm.invoke(
        textwrap.dedent(
            f"""
            You are an expert copywriter.
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
            
            Only respond with the response text, no other text or formatting.
            """
        )
    )
    return response.content