from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from traceback import format_exc
import uvicorn

# Import your core RIK modules
import main
import memory
import meta

app = FastAPI(
    title="Recursive Intelligence Kernel API",
    description="FastAPI wrapper exposing the RIK reasoning and feedback endpoints.",
    version="5.2.1"
)


class TaskRequest(BaseModel):
    task: str


@app.post("/run_task")
def run_task(req: TaskRequest):
    """
    Execute a recursive reasoning run on the given task with safe exception handling.
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        print(f"[INFO] Received task: {req.task}")
        result = main.recursive_run(req.task)
        print(f"[SUCCESS] Recursive run completed.")
        return {"timestamp": timestamp, "task": req.task, "result": result}
    except Exception as e:
        error_trace = format_exc()
        print(f"[ERROR] Recursive run failed: {e}\n{error_trace}")
        return {
            "timestamp": timestamp,
            "task": req.task,
            "error": str(e),
            "traceback": error_trace
        }


@app.get("/metrics")
def get_metrics():
    """
    Return current architecture fitness metrics from the Meta-Controller.
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        metrics = meta.evaluate_fitness()
        return {"timestamp": timestamp, "metrics": metrics}
    except Exception as e:
        error_trace = format_exc()
        print(f"[ERROR] Failed to fetch metrics: {e}\n{error_trace}")
        return {
            "timestamp": timestamp,
            "error": str(e),
            "traceback": error_trace
        }


@app.get("/memory")
def get_memory():
    """
    Retrieve recent episodic memory summaries.
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        episodes = memory.get_recent_episodes(limit=5)
        return {"timestamp": timestamp, "episodes": episodes}
    except Exception as e:
        error_trace = format_exc()
        print(f"[ERROR] Failed to retrieve memory: {e}\n{error_trace}")
        return {
            "timestamp": timestamp,
            "error": str(e),
            "traceback": error_trace
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)