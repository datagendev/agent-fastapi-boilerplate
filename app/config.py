"""Configuration management using Pydantic Settings."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required
    anthropic_api_key: str = Field(
        ..., description="Anthropic API key for Claude agent execution"
    )

    # Agent selection (optional)
    agent_name: Optional[str] = Field(
        default="default", description="Name of agent to load from .claude/agents/ directory"
    )
    agent_file_path: Optional[Path] = Field(
        default=None, description="Explicit path to agent.md file (overrides agent_name)"
    )

    # MCP Integration (optional)
    datagen_api_key: Optional[str] = Field(
        default=None, description="DataGen API key for MCP integration"
    )

    # Security (optional)
    webhook_secret: Optional[str] = Field(
        default=None, description="API key for webhook authentication"
    )

    # Model configuration (optional)
    model_name: str = Field(
        default="claude-sonnet-4-5",
        description="Claude model to use (overrides agent.md frontmatter)",
    )

    # Application settings
    log_level: str = Field(default="INFO", description="Logging level")
    port: int = Field(default=8000, description="Server port")
    permission_mode: str = Field(
        default="bypassPermissions",
        description="Agent SDK permission mode (safe with non-root Docker user)",
    )

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        """Ensure Anthropic API key is set."""
        if not v or not v.strip():
            raise ValueError(
                "ANTHROPIC_API_KEY is required. Set it in .env or as environment variable."
            )
        return v.strip()

    @field_validator("agent_file_path")
    @classmethod
    def validate_agent_path(cls, v: Optional[Path]) -> Optional[Path]:
        """Convert string to Path if needed."""
        if v is None:
            return None
        if isinstance(v, str):
            return Path(v)
        return v


# Global settings instance
settings = Settings()
