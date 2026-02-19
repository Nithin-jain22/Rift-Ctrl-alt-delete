import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from orchestrator import run_agent

app = FastAPI(title="Autonomous DevOps Agent")

# In-memory job store
job_store = {}


# Request model
class RunRequest(BaseModel):
    githubUrl: str
    teamName: str
    leaderName: str


@app.post("/run-agent")
def run_agent_endpoint(request: RunRequest, background_tasks: BackgroundTasks):
    # Generate unique job id
    job_id = str(uuid.uuid4())

    # Initialize job state
    job_store[job_id] = {
        "status": "running",
        "runSummary": None,
        "score": None,
        "fixes": [],
        "timeline": [],
        "error": None,
    }

    # Start background task
    background_tasks.add_task(
        run_agent,
        request.githubUrl,
        request.teamName,
        request.leaderName,
        job_id,
        job_store,
    )

    # Return immediately
    return {"job_id": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = job_store.get(job_id)

    if not job:
        return {"status": "not_found"}

    return job