"""
RIK API - Production-Ready Version
==================================

Enhanced with:
- Professional structured logging
- Request ID tracking
- API key authentication
- Rate limiting
- Input validation
- Health/monitoring endpoints
- CORS support
- Error handling
"""

from fastapi import FastAPI, HTTPException, Request, Security, status, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
import uvicorn
import time
from collections import defaultdict

# Import configuration and logging
from config import config
from logging_config import get_logger, LogTimer, generate_request_id

# Import core RIK modules
import main
import memory
import meta
from selector_recovery import recover_selector, test_selector
from invoice_processor import process_invoice, get_automation_stats

# Get logger
logger = get_logger(__name__)

# ============================================================================
# FASTAPI APP with Enhanced Configuration
# ============================================================================

app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    contact={
        "name": "RIK Support",
        "email": "support@rik-ai.com",
    },
    license_info={
        "name": "Commercial License",
    },
)

# ============================================================================
# CORS Middleware
# ============================================================================

if config.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS enabled", extra={"origins": config.CORS_ORIGINS})

# ============================================================================
# Request ID Middleware
# ============================================================================

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracking"""
    request_id = generate_request_id()
    request.state.request_id = request_id

    # Add to logger context
    logger_with_id = get_logger(__name__)
    logger_with_id.set_request_id(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# ============================================================================
# Performance Timing Middleware
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_seconds": duration,
            "client_host": request.client.host if request.client else "unknown",
        }
    )

    return response

# ============================================================================
# API Authentication
# ============================================================================

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limiting storage (in-memory, for production use Redis)
rate_limit_storage = defaultdict(list)

def verify_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """
    Verify API key if authentication is enabled.

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not config.API_KEY_ENABLED:
        return "auth_disabled"  # Skip auth in development

    if not api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide via X-API-Key header."
        )

    if api_key not in config.API_KEYS:
        logger.warning("Invalid API key attempted", extra={"key_prefix": api_key[:8]})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    logger.debug("API key validated", extra={"key_prefix": api_key[:8]})
    return api_key

def check_rate_limit(request: Request, api_key: str = Depends(verify_api_key)):
    """
    Simple rate limiting (requests per period).

    For production, use Redis-based rate limiting.
    """
    if not config.RATE_LIMIT_ENABLED:
        return

    now = time.time()
    client_key = api_key if api_key != "auth_disabled" else request.client.host

    # Clean old entries
    rate_limit_storage[client_key] = [
        timestamp for timestamp in rate_limit_storage[client_key]
        if now - timestamp < config.RATE_LIMIT_PERIOD
    ]

    # Check limit
    if len(rate_limit_storage[client_key]) >= config.RATE_LIMIT_REQUESTS:
        logger.warning(
            "Rate limit exceeded",
            extra={"client": client_key, "requests": len(rate_limit_storage[client_key])}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {config.RATE_LIMIT_REQUESTS} requests per {config.RATE_LIMIT_PERIOD}s"
        )

    # Record this request
    rate_limit_storage[client_key].append(now)

# ============================================================================
# REQUEST/RESPONSE MODELS (Enhanced with Validation)
# ============================================================================

class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=1000, description="Task description")

    @field_validator('task')
    @classmethod
    def task_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Task cannot be empty")
        return v


class SelectorRecoveryRequest(BaseModel):
    """Request model for web scraper selector recovery"""
    failed_selector: str = Field(..., min_length=1, max_length=500)
    html: str = Field(..., min_length=1, max_length=10_000_000)  # 10MB limit
    url: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = None


class SelectorTestRequest(BaseModel):
    """Request model for testing a selector"""
    selector: str = Field(..., min_length=1, max_length=500)
    html: str = Field(..., min_length=1, max_length=10_000_000)
    selector_type: str = Field("css", pattern="^(css|xpath)$")


class InvoiceProcessRequest(BaseModel):
    """Request model for invoice processing with exception handling"""
    pdf_content: str = Field(..., min_length=1, max_length=1_000_000)
    invoice_id: Optional[str] = Field(None, max_length=100)
    context: Optional[Dict[str, Any]] = None

    @field_validator('invoice_id')
    @classmethod
    def validate_invoice_id(cls, v):
        if v and not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Invoice ID contains invalid characters")
        return v


# ============================================================================
# HEALTH & MONITORING ENDPOINTS
# ============================================================================

@app.get("/health/live", tags=["Monitoring"])
def liveness_check():
    """
    Kubernetes liveness probe - Is the service alive?

    Returns 200 if service is running, regardless of readiness.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": config.ENVIRONMENT
    }


@app.get("/health/ready", tags=["Monitoring"])
def readiness_check():
    """
    Kubernetes readiness probe - Is the service ready to handle requests?

    Checks:
    - Database connectivity
    - Memory system functional

    Returns 200 if ready, 503 if not ready.
    """
    checks = {}

    # Check database
    try:
        # Simple database check
        memory.get_recent_episodes(limit=1)
        checks["database"] = True
    except Exception as e:
        logger.error("Database health check failed", exc_info=True)
        checks["database"] = False

    # Check memory system
    try:
        memory.retrieve_context("health_check_test")
        checks["memory"] = True
    except Exception as e:
        logger.error("Memory health check failed", exc_info=True)
        checks["memory"] = False

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.get("/health", tags=["Monitoring"])
def health_check():
    """Simple health check endpoint (legacy, use /health/live or /health/ready)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": config.API_VERSION,
        "environment": config.ENVIRONMENT,
        "features": [
            "selector_recovery",
            "invoice_processing",
            "exception_handling",
            "memory",
            "metrics",
            "reasoning"
        ]
    }


@app.get("/version", tags=["Monitoring"])
def get_version():
    """Get API version and build info"""
    return {
        "version": config.API_VERSION,
        "environment": config.ENVIRONMENT,
        "debug": config.DEBUG,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# CORE ENDPOINTS (with logging and auth)
# ============================================================================

@app.post("/run_task", tags=["Core"], dependencies=[Depends(check_rate_limit)])
def run_task(req: TaskRequest, request: Request):
    """
    Execute a recursive reasoning run on the given task with safe exception handling.
    """
    request_id = request.state.request_id

    with LogTimer(logger, "Recursive reasoning", task=req.task, request_id=request_id):
        try:
            logger.info("Received task", extra={"task": req.task, "request_id": request_id})

            result = main.recursive_run(req.task)

            logger.info("Task completed successfully", extra={"request_id": request_id})

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "task": req.task,
                "result": result
            }

        except Exception as e:
            logger.error(
                "Task failed",
                exc_info=True,
                extra={"task": req.task, "request_id": request_id}
            )
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", tags=["Monitoring"], dependencies=[Depends(check_rate_limit)])
def get_metrics(request: Request):
    """
    Return current architecture fitness metrics from the Meta-Controller.
    """
    request_id = request.state.request_id

    try:
        metrics = meta.evaluate_fitness()
        logger.debug("Metrics retrieved", extra={"request_id": request_id})
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "metrics": metrics
        }
    except Exception as e:
        logger.error("Failed to fetch metrics", exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory", tags=["Memory"], dependencies=[Depends(check_rate_limit)])
def get_memory(request: Request, limit: int = 5):
    """
    Retrieve recent episodic memory summaries.
    """
    request_id = request.state.request_id

    try:
        episodes = memory.get_recent_episodes(limit=limit)
        logger.debug("Memory retrieved", extra={"request_id": request_id, "count": len(episodes)})
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "episodes": episodes
        }
    except Exception as e:
        logger.error("Failed to retrieve memory", exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recover_selector", tags=["Web Scraping"], dependencies=[Depends(check_rate_limit)])
def recover_web_scraper_selector(req: SelectorRecoveryRequest, request: Request):
    """
    **RIK Self-Healing Web Scraper Endpoint**

    When a web scraper's CSS/XPath selector fails, this endpoint:
    1. Diagnoses why the selector failed
    2. Analyzes the HTML structure
    3. Generates alternative selectors ranked by confidence
    4. Logs the recovery attempt to memory for learning
    """
    request_id = request.state.request_id

    with LogTimer(
        logger,
        "Selector recovery",
        selector=req.failed_selector,
        url=req.url,
        request_id=request_id
    ):
        try:
            logger.info(
                "Selector recovery requested",
                extra={
                    "selector": req.failed_selector,
                    "url": req.url,
                    "html_length": len(req.html),
                    "request_id": request_id
                }
            )

            result = recover_selector(
                failed_selector=req.failed_selector,
                html=req.html,
                url=req.url,
                context=req.context
            )

            logger.info(
                "Selector recovery completed",
                extra={
                    "alternatives_count": result['total_alternatives'],
                    "recommended": result['recommended']['selector'] if result['recommended'] else None,
                    "request_id": request_id
                }
            )

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "success": True,
                **result
            }

        except Exception as e:
            logger.error("Selector recovery failed", exc_info=True, extra={"request_id": request_id})
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/test_selector", tags=["Web Scraping"], dependencies=[Depends(check_rate_limit)])
def test_web_scraper_selector(req: SelectorTestRequest, request: Request):
    """
    Test if a specific selector works on given HTML.
    """
    request_id = request.state.request_id

    try:
        result = test_selector(
            selector=req.selector,
            html=req.html,
            selector_type=req.selector_type
        )

        logger.debug(
            "Selector tested",
            extra={
                "selector": req.selector,
                "success": result['success'],
                "count": result.get('count', 0),
                "request_id": request_id
            }
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "selector": req.selector,
            "selector_type": req.selector_type,
            **result
        }

    except Exception as e:
        logger.error("Selector test failed", exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process_invoice", tags=["Invoice Processing"], dependencies=[Depends(check_rate_limit)])
def process_invoice_endpoint(req: InvoiceProcessRequest, request: Request):
    """
    **RIK Invoice Exception Handler Endpoint**

    Processes invoices with intelligent exception handling using RIK's reasoning engine.

    Traditional RPA: 40% exception rate → all require manual intervention
    RIK: 40% exception rate → 80% auto-resolved through reasoning
    """
    request_id = request.state.request_id

    with LogTimer(
        logger,
        "Invoice processing",
        invoice_id=req.invoice_id,
        request_id=request_id
    ):
        try:
            logger.info(
                "Invoice processing requested",
                extra={
                    "invoice_id": req.invoice_id,
                    "content_length": len(req.pdf_content),
                    "request_id": request_id
                }
            )

            result = process_invoice(
                pdf_content=req.pdf_content,
                invoice_id=req.invoice_id,
                context=req.context
            )

            logger.info(
                "Invoice processed",
                extra={
                    "invoice_id": result['invoice_id'],
                    "final_action": result['final_action'],
                    "exceptions_found": result['exceptions_found'],
                    "traditional_rpa_would_fail": result['traditional_rpa_would_fail'],
                    "processing_time": result['processing_time_seconds'],
                    "request_id": request_id
                }
            )

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "success": True,
                **result
            }

        except Exception as e:
            logger.error(
                "Invoice processing failed",
                exc_info=True,
                extra={"invoice_id": req.invoice_id, "request_id": request_id}
            )
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/invoice_stats", tags=["Invoice Processing"], dependencies=[Depends(check_rate_limit)])
def get_invoice_automation_stats(request: Request):
    """
    Get invoice automation statistics showing RIK's value.

    This is the "money slide" - shows measurable ROI of RIK.
    """
    request_id = request.state.request_id

    try:
        stats = get_automation_stats()

        # Calculate ROI metrics
        traditional_manual_interventions = stats['invoices_with_exceptions']
        rik_manual_interventions = stats['exceptions_escalated']
        interventions_saved = traditional_manual_interventions - rik_manual_interventions

        cost_per_intervention = 20
        monthly_savings = interventions_saved * cost_per_intervention

        logger.debug("Invoice stats retrieved", extra={"request_id": request_id})

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "stats": stats,
            "roi": {
                "interventions_saved": interventions_saved,
                "cost_per_intervention": cost_per_intervention,
                "monthly_savings_usd": monthly_savings,
                "annual_savings_usd": monthly_savings * 12,
                "automation_improvement": f"{(stats['automation_rate'] - stats['traditional_rpa_automation_rate']) * 100:.0f}%"
            }
        }

    except Exception as e:
        logger.error("Failed to fetch invoice stats", exc_info=True, extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup"""
    logger.info(
        "RIK API starting",
        extra={
            "version": config.API_VERSION,
            "environment": config.ENVIRONMENT,
            "debug": config.DEBUG,
            "api_key_enabled": config.API_KEY_ENABLED,
            "rate_limit_enabled": config.RATE_LIMIT_ENABLED,
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info("RIK API shutting down")


# ============================================================================
# MAIN (for running directly)
# ============================================================================

if __name__ == "__main__":
    logger.info(
        f"Starting RIK API server",
        extra={
            "host": config.API_HOST,
            "port": config.API_PORT,
            "workers": config.API_WORKERS,
            "reload": config.API_RELOAD
        }
    )

    uvicorn.run(
        "rik_api_enhanced:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD,
        log_level=config.LOG_LEVEL.lower()
    )
