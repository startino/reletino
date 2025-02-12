import asyncio

import logging
import os
import threading
from time import sleep

from dotenv import load_dotenv
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from src.lib.graph.project_setup import ProfileGraph
from src.lib.graph.project_setup.node.drafter import RecommendationOutput
from src.lib.graph.project_setup.state import Context, ProfileState
from src.lib.graph.project_setup.tools.web_scraper import web_scraper
from src.lib.reddit_profile_analysis import analyze_reddit_user
from src.models.simple_submission import SimpleSubmission
from supabase import create_client

from src.interfaces import db
from src.models.project import Project
from src.lib.reddit_worker import RedditStreamWorker
from src.lib.autofill_project import autofill_form, FormField
from src.lib.generate_response import generate_response
from praw.models import Submission

from sse_starlette import EventSourceResponse

load_dotenv()

REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")

if REDDIT_PASSWORD is None:
    raise ValueError("REDDIT_PASSWORD is not set")

if REDDIT_USERNAME is None:
    raise ValueError("REDDIT_USERNAME is not set")

workers = {}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(_: FastAPI):
    supabase = db.client()

    # project_res = supabase.table("projects").select("*").eq("running", True).execute()
        
    # for project_data in project_res.data:
        
    #     profile_res = supabase.table("profiles").select("*, environments (*)").eq("id", project_data["profile_id"]).execute()
    #     logging.info(f"Profile: {profile_res.data}")
    #     project = Project(**project_data)
    #     worker, _ = workers.get(project.id, (None, None))
                
    #     # Project wasn't properly started
    #     if project.running and worker is None:
    #         logging.info(f"Starting project stream for project: {project.id}")
    #         start_project_stream(StartStreamRequest(project=project, environment_name=profile_res.data[0]["environments"][0]["name"]))
        
    #     # Project was stopped but the worker is still running
    #     if not project.running and worker is not None:
    #         logging.info(f"Stopping project stream for project: {project.id}")
    #         stop_project_stream(StopStreamRequest(project_id=project.id))
            
    yield
    
    # Clean up the threads
    for project_id, (worker, thread) in workers.items():
        logging.info(f"Stopping worker for project: {project_id}")
        worker.stop()
        thread.join(timeout=10)  # Waits 10 seconds for the thread to finish

        if thread.is_alive():
            logging.error(f"Thread for Reddit worker didn't stop in time. Project: {project_id}")
        else:
            logging.info(f"Successfully stopped worker for project: {project_id}")

    workers.clear()  # Clear the workers dictionary


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def redirect_to_docs():
    logging.info("Redirecting to /docs")
    return RedirectResponse(url="/docs")


class StartStreamRequest(BaseModel):
    project: Project
    team_name: str


@app.post("/start")
def start_project_stream(q: StartStreamRequest):
    if q.project.id in workers:
        logging.info(f"Restarting project stream for project: {q.project.id}")
        stop_project_stream(StopStreamRequest(project_id=q.project.id))

    worker = RedditStreamWorker(project=q.project, team_name=q.team_name)
    thread = threading.Thread(target=worker.start)
    workers[q.project.id] = (worker, thread)
    thread.start()
    logging.info(f"Started project stream: {q.project.id}")
    return {"status": "success", "message": "Stream started"}


class StopStreamRequest(BaseModel):
    project_id: str


@app.post("/stop")
def stop_project_stream(q: StopStreamRequest):
    worker, thread = workers.get(q.project_id, (None, None))
    
    if worker is None:
        logging.error(f"Worker not found for project: {q.project_id}")
        return {"status": "success", "message": "Stream not found (probably already stopped or never started)"}
    
    worker.stop()
    thread.join(timeout=10)  # Waits 10 seconds for the thread to finish

    if thread.is_alive():
        logging.error(f"Thread for Reddit worker didn't stop in time. Project: {q.project_id}")

    del workers[q.project_id]  # Cleanup
    logging.info(f"Stopped project stream: {q.project_id}")

    return {"status": "success", "message": "Stream stopped"}


class SetupProjectRequest(BaseModel):
    url: str | None = None
    description: str | None = None
    objective: Literal["find_leads", "find_competitors", "find_ideas", "find_influencers", "find_investors", "find_partners"]
    mode: Literal["standard", "advanced"]


@app.post("/setup-project")
async def setup_project(q: SetupProjectRequest):
    if q.url is not None:
        link_or_profile = "link"
    elif q.description is not None:
        link_or_profile = "description"
    else:
        raise HTTPException(status_code=400, detail="Either url or description must be provided")

    context = Context(
        type=link_or_profile,
        value=str(q.url if link_or_profile == "link" else q.description)
    )

    if context.type == "link":
        context.value = f"# URL: \n{context.value}" + f"## URL DATA: \n{web_scraper(context.value)}"
    
    initial_state = ProfileState(
        context=context,
        objective=q.objective,
        messages=[],
        mode=q.mode  # Pass mode to state
    )
    
    graph = ProfileGraph(initial_state).graph()
  
    final_state = await graph.ainvoke(initial_state)
    
    parsed_results = RecommendationOutput(**final_state["messages"][-1].tool_calls[0]["args"])

    return {
        "project_name": parsed_results.project_name,
        "subreddits": [subreddit.name for subreddit in parsed_results.subreddits],
        "filtering_prompt": parsed_results.filtering_prompt,
    }

class GenerateResponseRequest(BaseModel):
    author_name: str
    project_id: str
    submission_title: str
    submission_selftext: str
    team_name: str
    is_dm: bool = False
    feedback: str = ""

@app.post("/generate-response")
def generate_project_response(q: GenerateResponseRequest):
    try:
        logging.info(f"Generating response for project {q.project_id}, isDM: {q.is_dm}")
        simple_submission = SimpleSubmission(
            title=q.submission_title,
            selftext=q.submission_selftext,
            author_name=q.author_name
        )
        response = generate_response(
            simple_submission, 
            team_name=q.team_name, 
            project_id=q.project_id, 
            is_dm=q.is_dm,
            feedback=q.feedback
        )
        logging.info("Response generated successfully")
        return {"status": "success", "response": response}
    except Exception as e:
        logging.error(f"Error generating response: {e}", exc_info=True)  # Add full traceback
        return {"status": "error", "message": str(e)}

class ProfileAnalysisRequest(BaseModel):
    username: str

@app.post("/analyze-profile")
async def analyze_profile(request: ProfileAnalysisRequest):
    """
    Analyze a Reddit user's profile and return insights
    """
    try:
        if not request.username:
            raise HTTPException(status_code=400, detail="Username is required")
            
        analysis = analyze_reddit_user(request.username, "")  # Empty project prompt since we're just analyzing the profile
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Profile not found or has been deleted")
            
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Error analyzing profile for {request.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze profile: {str(e)}") 