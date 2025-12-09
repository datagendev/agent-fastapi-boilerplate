"""Pydantic models for request/response schemas."""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """Request model for agent execution - accepts any JSON payload."""

    payload: Dict[str, Any] = Field(
        ...,
        description="Arbitrary JSON data passed to the agent",
        examples=[
            {"email": "user@example.com", "task": "enrich profile"},
            {"text": "Hello world", "action": "analyze"},
        ],
    )


class RunResponse(BaseModel):
    """Response model for agent execution."""

    status: Literal["queued", "completed", "failed"] = Field(
        ..., description="Execution status"
    )
    request_id: str = Field(..., description="Unique request identifier")
    message: str = Field(..., description="Human-readable status message")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Agent execution result (if completed synchronously)"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: Literal["ok", "error"] = Field(..., description="Service health status")
    agent_name: str = Field(..., description="Name of the loaded agent")
    model: str = Field(..., description="Claude model being used")
    ready: bool = Field(..., description="Whether the agent is ready to process requests")


class AgentMetadata(BaseModel):
    """Agent metadata from frontmatter."""

    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(default=None, description="Agent description")
    tools: list[str] = Field(default_factory=list, description="Allowed tools")
    model: str = Field(..., description="Claude model")
