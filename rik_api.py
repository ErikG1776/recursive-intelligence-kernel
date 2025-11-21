"""
rik_api.py | Recursive Intelligence Kernel API
-----------------------------------------------
FastAPI wrapper exposing the RIK reasoning and feedback endpoints.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from traceback import format_exc
from typing import Optional
import uvicorn

from config import setup_logging, API_HOST, API_PORT
import main
import memory
import meta
from db import create_indexes

logger = setup_logging("rik.api")

app = FastAPI(
    title="Recursive Intelligence Kernel API",
    description="FastAPI wrapper exposing the RIK reasoning and feedback endpoints.",
    version="5.2.1"
)


# ==========================================================
# === Request/Response Models ==============================
# ==========================================================

class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=10000, description="Task to process")


class MemoryRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=100, description="Number of episodes to retrieve")


# ==========================================================
# === Startup Events =======================================
# ==========================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup."""
    logger.info("Initializing RIK API...")
    create_indexes()
    memory.init_memory_db()
    logger.info("RIK API initialized successfully")


# ==========================================================
# === API Endpoints ========================================
# ==========================================================

@app.post("/run_task")
def run_task(req: TaskRequest):
    """
    Execute a recursive reasoning run on the given task with safe exception handling.
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        logger.info(f"Received task: {req.task[:100]}...")
        result = main.recursive_run(req.task)
        logger.info("Recursive run completed successfully")
        return {"timestamp": timestamp, "task": req.task, "result": result}
    except Exception as e:
        error_trace = format_exc()
        logger.error(f"Recursive run failed: {e}")
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
        logger.error(f"Failed to fetch metrics: {e}")
        return {
            "timestamp": timestamp,
            "error": str(e),
            "traceback": error_trace
        }


@app.get("/memory")
def get_memory(limit: int = 5):
    """
    Retrieve recent episodic memory summaries.
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        episodes = memory.get_recent_episodes(limit=min(limit, 100))
        return {"timestamp": timestamp, "episodes": episodes, "count": len(episodes)}
    except Exception as e:
        error_trace = format_exc()
        logger.error(f"Failed to retrieve memory: {e}")
        return {
            "timestamp": timestamp,
            "error": str(e),
            "traceback": error_trace
        }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "5.2.1"
    }


@app.get("/fitness/history")
def get_fitness_history(limit: int = 10):
    """Get historical fitness evaluations."""
    try:
        history = meta.get_fitness_history(limit=min(limit, 100))
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to retrieve fitness history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
