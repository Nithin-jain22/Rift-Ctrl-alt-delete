import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

from core.orchestrator import run_agent as core_run_agent

load_dotenv()

app = FastAPI(title="Autonomous DevOps Agent")

# Enable CORS (for local frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job tracking
job_store: Dict[str, Dict[str, Any]] = {}


# ==============================
# Request Schema
# ==============================
class RunRequest(BaseModel):
    githubUrl: str
    teamName: str
    leaderName: str


# ==============================
# Background Runner
# ==============================
def background_runner(repo_url: str, team_name: str, leader_name: str, job_id: str):
    try:
        result = core_run_agent(repo_url, team_name, leader_name)

        job_store[job_id] = {
            "status": "completed",
            "runSummary": {
                "repository": result.get("repository"),
                "branch": result.get("branch"),
                "teamName": team_name,
                "leaderName": leader_name,
                "totalFailures": result.get("total_failures"),
                "fixesApplied": result.get("fixes_applied"),
                "ciStatus": result.get("ci_status"),
                "totalTime": result.get("total_time"),
            },
            "score": result.get("score"),
            "fixes": result.get("fixes"),
            "timeline": result.get("timeline"),
            "retryLimit": result.get("retry_limit"),
            "error": None,
        }

    except Exception as e:
        job_store[job_id] = {
            "status": "failed",
            "runSummary": None,
            "score": None,
            "fixes": [],
            "timeline": [],
            "error": str(e),
        }


# ==============================
# POST Endpoint
# ==============================
@app.post("/run-agent")
def run_agent_endpoint(request: RunRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    job_store[job_id] = {
        "status": "running",
        "runSummary": None,
        "score": None,
        "fixes": [],
        "timeline": [],
        "error": None,
    }

    background_tasks.add_task(
        background_runner,
        request.githubUrl,
        request.teamName,
        request.leaderName,
        job_id,
    )

    return {"jobId": job_id}


# ==============================
# Status Endpoint
# ==============================
@app.get("/status/{job_id}")
def get_status(job_id: str):
    return job_store.get(job_id, {"status": "not_found"})