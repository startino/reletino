import asyncio
import json
import logging
import os
import threading
from time import sleep
from uuid import UUID, uuid4
from dotenv import load_dotenv
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse

from src.models.project import Project
from src.models import PublishCommentRequest, GenerateCommentRequest, FalseLead, Lead
from src.reddit_worker import RedditStreamWorker

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

app = FastAPI()

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

@app.post("/start")
def start_project_stream(project: Project):
    worker = RedditStreamWorker(project=project)
    thread = threading.Thread(target=worker.start)
    workers[project.id] = (worker, thread)
    thread.start()
    logging.info(f"Started project stream: {project.id}")
    return {"status": "success", "message": "Stream started"}

class StopStreamRequest(BaseModel):
    project_id: str

@app.post("/stop")
def stop_project_stream(stop_request: StopStreamRequest):
    worker, thread = workers.get(stop_request.project_id, (None, None))
    
    if worker is None:
        logging.error(f"Worker not found for project: {stop_request.project_id}")
        return {"status": "success", "message": "Stream not found (probably already stopped or never started)"}
    
    worker.stop()
    thread.join(timeout=10)  # Waits 10 seconds for the thread to finish

    if thread.is_alive():
        logging.error(f"Thread for Reddit worker didn't stop in time. Project: {stop_request.project_id}")

    del workers[stop_request.project_id]  # Cleanup
    logging.info(f"Stopped project stream: {stop_request.project_id}")

    return {"status": "success", "message": "Stream stopped"}