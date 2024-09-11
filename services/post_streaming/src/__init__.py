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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def redirect_to_docts():
    return RedirectResponse(url="/docs")


class StartStreamRequest(BaseModel):
    subreddits: list[str] = ["SaaS", "SaaSy", "startups", "YoungEntrepreneurs", "NoCodeSaas", "nocode", "cofounder", "Entrepreneur", "futino"]
    
    
@app.post("/start")
def start_stream(start_request: StartStreamRequest):
    worker_id = str(uuid4())
    worker = RedditStreamWorker(start_request.subreddits, REDDIT_USERNAME, REDDIT_PASSWORD)
    thread = threading.Thread(target=worker.start)
    workers[worker_id] = (worker, thread)
    thread.start()
    return {"worker_id": worker_id}


@app.post("/stop/{worker_id}")
def stop_stream(worker_id: str):
    worker, thread = workers.get(worker_id, (None, None))
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.stop()
    thread.join(timeout=10)  # Waits 10 seconds for the thread to finish

    if thread.is_alive():
        logging.error(f"Thread for Reddit worker didn't stop in time")

    del workers[worker_id]  # Cleanup

    return {"message": "Stream stopped"}
