import json
from praw import Submission
from src.models import Evaluation
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

test_submission = Submission(
    id="1",
    title="test",
    selftext="test",
    subreddit="test",
    author="test",
    created_utc=0,
)

existing_submission = supabase.table("submissions").select("*").eq("praw_submission_object", json.loads(json.dumps(test_submission, default=str))).execute()

evaluation = Evaluation(
    relevant=True,
    question="test",
)

if len(existing_submission.data) > 0:
   print("existing")

supabase.table("submissions").insert(
    {
        "praw_submission_object": test_submission.model_dump(),
        "evaluation": evaluation.model_dump(),
    }
).execute()