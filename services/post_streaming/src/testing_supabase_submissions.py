import json
from praw.models import Submission
from models import Evaluation
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

test_submission = Submission()

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