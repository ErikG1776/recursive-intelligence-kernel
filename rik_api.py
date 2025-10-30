from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from traceback import format_exc
from typing import Optional, Dict, Any
import uvicorn

# Import your core RIK modules
import main
import memory
import meta
from selector_recovery import recover_selector, test_selector

app = FastAPI(
    title="Recursive Intelligence Kernel API",
    description="FastAPI wrapper exposing the RIK reasoning and feedback endpoints.",
    version="5.3.0"
)


class TaskRequest(BaseModel):
    task: str


class SelectorRecoveryRequest(BaseModel):
    """Request model for web scraper selector recovery"""
    failed_selector: str
    html: str
    url: str
    context: Optional[Dict[str, Any]] = None


class SelectorTestRequest(BaseModel):
    """Request model for testing a selector"""
    selector: str
    html: str
    selector_type: str = "css"  # css or xpath


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


@app.post("/recover_selector")
def recover_web_scraper_selector(req: SelectorRecoveryRequest):
    """
    **RIK Self-Healing Web Scraper Endpoint**

    When a web scraper's CSS/XPath selector fails, this endpoint:
    1. Diagnoses why the selector failed
    2. Analyzes the HTML structure
    3. Generates alternative selectors ranked by confidence
    4. Logs the recovery attempt to memory for learning

    Use Case: n8n workflows can call this when scraping fails, get alternative
    selectors, and retry automatically - achieving self-healing automation.

    Returns:
        - original_selector: The selector that failed
        - alternatives: List of alternative selectors with confidence scores
        - recommended: The highest-confidence alternative
        - diagnosis: RIK's analysis of why the original failed
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        print(f"[INFO] Selector recovery requested for: {req.failed_selector}")
        print(f"[INFO] URL: {req.url}")
        print(f"[INFO] HTML length: {len(req.html)} chars")

        result = recover_selector(
            failed_selector=req.failed_selector,
            html=req.html,
            url=req.url,
            context=req.context
        )

        print(f"[SUCCESS] Generated {result['total_alternatives']} alternatives")
        if result['recommended']:
            print(f"[INFO] Recommended: {result['recommended']['selector']} "
                  f"({result['recommended']['strategy']}, "
                  f"confidence: {result['recommended']['confidence']})")

        return {
            "timestamp": timestamp,
            "success": True,
            **result
        }

    except Exception as e:
        error_trace = format_exc()
        print(f"[ERROR] Selector recovery failed: {e}\n{error_trace}")
        return {
            "timestamp": timestamp,
            "success": False,
            "error": str(e),
            "traceback": error_trace
        }


@app.post("/test_selector")
def test_web_scraper_selector(req: SelectorTestRequest):
    """
    Test if a specific selector works on given HTML.

    Useful for validating that a recovered selector actually works before
    using it in production.

    Returns:
        - success: Whether selector found any elements
        - count: Number of elements found
        - samples: Sample text from first 3 elements
    """
    timestamp = datetime.utcnow().isoformat()
    try:
        result = test_selector(
            selector=req.selector,
            html=req.html,
            selector_type=req.selector_type
        )

        return {
            "timestamp": timestamp,
            "selector": req.selector,
            "selector_type": req.selector_type,
            **result
        }

    except Exception as e:
        error_trace = format_exc()
        print(f"[ERROR] Selector test failed: {e}\n{error_trace}")
        return {
            "timestamp": timestamp,
            "success": False,
            "error": str(e),
            "traceback": error_trace
        }


@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "5.3.0",
        "features": ["selector_recovery", "memory", "metrics", "reasoning"]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)