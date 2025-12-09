"""FastAPI application entry point."""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.agent import agent_executor, log_event
from app.config import settings
from app.models import AgentMetadata, HealthResponse, RunRequest, RunResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    log_event("app_startup", agent=agent_executor.config.name, model=agent_executor.model)
    yield
    log_event("app_shutdown")


app = FastAPI(
    title="Agent API",
    description="FastAPI boilerplate for deploying Claude Code agents",
    version="1.0.0",
    lifespan=lifespan,
)


# Middleware: Request ID injection
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to all requests."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log incoming request
    log_event(
        "http_request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    response = await call_next(request)

    # Log response
    log_event(
        "http_response",
        request_id=request_id,
        status_code=response.status_code,
    )

    return response


# Middleware: Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with structured logging."""
    request_id = getattr(request.state, "request_id", "unknown")

    log_event(
        "http_error",
        request_id=request_id,
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "request_id": request_id,
            "message": "Internal server error",
            "detail": str(exc) if settings.log_level.upper() == "DEBUG" else None,
        },
    )


# Dependency: API key verification
async def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")):
    """Verify API key from request header.

    If WEBHOOK_SECRET is not set, authentication is optional (for development).
    In production, always set WEBHOOK_SECRET.
    """
    if not settings.webhook_secret:
        # No secret configured - allow unauthenticated access
        return

    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API key required. Provide X-API-Key header.",
        )

    if x_api_key != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid API key")


# Background task: Agent execution
async def run_agent_task(payload: dict, request_id: str):
    """Execute agent in background."""
    try:
        await agent_executor.execute(payload, request_id)
    except Exception as e:
        log_event(
            "background_task_error",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__,
        )


# Endpoints
@app.post("/run", response_model=RunResponse)
async def run_agent(
    request: RunRequest,
    background_tasks: BackgroundTasks,
    req: Request,
    _: None = Depends(verify_api_key),
):
    """Execute agent with JSON payload.

    Accepts any JSON payload and queues agent execution in the background.
    Returns immediately with a request ID for tracking.

    Requires X-API-Key header if WEBHOOK_SECRET is set in environment.
    """
    request_id = req.state.request_id

    log_event(
        "agent_queued",
        request_id=request_id,
        agent=agent_executor.config.name,
        payload_keys=list(request.payload.keys()),
    )

    # Queue background task
    background_tasks.add_task(run_agent_task, request.payload, request_id)

    return RunResponse(
        status="queued",
        request_id=request_id,
        message=f"Agent '{agent_executor.config.name}' is processing your request",
    )


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint.

    Returns agent configuration and readiness status.
    """
    return HealthResponse(
        status="ok",
        agent_name=agent_executor.config.name,
        model=agent_executor.model,
        ready=True,
    )


@app.get("/agent", response_model=AgentMetadata)
def get_agent_metadata():
    """Get agent metadata from frontmatter.

    Useful for debugging and discovery.
    """
    return AgentMetadata(
        name=agent_executor.config.name,
        description=agent_executor.config.description,
        tools=agent_executor.config.allowed_tools,
        model=agent_executor.model,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
