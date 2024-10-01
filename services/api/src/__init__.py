import asyncio

import logging
import os
import threading
from time import sleep

from dotenv import load_dotenv
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from supabase import create_client

from src.models.project import Project
from src.reddit_worker import RedditStreamWorker

load_dotenv()

REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")

if REDDIT_PASSWORD is None:
    raise ValueError("REDDIT_PASSWORD is not set")

if REDDIT_USERNAME is None:
    raise ValueError("REDDIT_USERNAME is not set")

workers = {}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(_: FastAPI):
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

    project_res = supabase.table("projects").select("*").eq("running", True).execute()
        
    for project_data in project_res.data:
        
        profile_res = supabase.table("profiles").select("*, environments (*)").eq("id", project_data["profile_id"]).execute()
        logging.info(f"Profile: {profile_res.data}")
        project = Project(**project_data)
        worker, _ = workers.get(project.id, (None, None))
                
        # Project wasn't properly started
        if project.running and worker is None:
            logging.info(f"Starting project stream for project: {project.id}")
            start_project_stream(StartStreamRequest(project=project, environment_name=profile_res.data[0]["environments"][0]["name"]))
        
        # Project was stopped but the worker is still running
        if not project.running and worker is not None:
            logging.info(f"Stopping project stream for project: {project.id}")
            stop_project_stream(StopStreamRequest(project_id=project.id))
            
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
    environment_name: str


@app.post("/start")
def start_project_stream(q: StartStreamRequest):
    if q.project.id in workers:
        logging.info(f"Restarting project stream for project: {q.project.id}")
        stop_project_stream(StopStreamRequest(project_id=q.project.id))

    worker = RedditStreamWorker(project=q.project, environment_name=q.environment_name)
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
