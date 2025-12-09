"""Agent loading and execution logic."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import frontmatter
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    ToolUseBlock,
    query,
)

from app.config import settings

logger = logging.getLogger(__name__)


def log_event(event: str, **data):
    """Emit structured JSON log for easy parsing."""
    payload = {"event": event, **data}
    logger.info(json.dumps(payload, indent=2, ensure_ascii=False))


@dataclass
class AgentConfig:
    """Configuration loaded from agent.md file."""

    name: str
    model: str
    system_prompt: str
    allowed_tools: list[str]
    description: Optional[str] = None

    @classmethod
    def from_file(cls, path: Path) -> "AgentConfig":
        """Load agent configuration from markdown file.

        Supports both:
        - agent.md with YAML frontmatter
        - prompt.md with just markdown content
        """
        if not path.exists():
            raise FileNotFoundError(f"Agent file not found: {path}")

        content = path.read_text(encoding="utf-8")

        # Try to parse YAML frontmatter
        try:
            post = frontmatter.loads(content)
            has_frontmatter = bool(post.metadata)
        except Exception:
            has_frontmatter = False
            post = None

        if has_frontmatter and post:
            # Extract metadata from frontmatter
            name = post.metadata.get("name", path.stem)
            model = post.metadata.get("model", "claude-sonnet-4-5")
            description = post.metadata.get("description")

            # Parse tools (can be comma-separated string or list)
            tools = post.metadata.get("tools", [])
            if isinstance(tools, str):
                allowed_tools = [t.strip() for t in tools.split(",") if t.strip()]
            else:
                allowed_tools = tools if isinstance(tools, list) else []

            # Use the markdown body as system prompt
            system_prompt = post.content.strip()
        else:
            # Plain markdown file without frontmatter
            name = path.stem
            model = "claude-sonnet-4-5"
            description = None
            allowed_tools = [
                "mcp__Datagen__getToolDetails",
                "mcp__Datagen__executeTool",
            ]
            system_prompt = content.strip()

        return cls(
            name=name,
            model=model,
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            description=description,
        )


def discover_agent_file() -> Path:
    """Discover agent file based on configuration.

    Precedence:
    1. AGENT_FILE_PATH (explicit path)
    2. .claude/agents/{AGENT_NAME}.md
    3. Auto-detect single .md file in .claude/agents/
    4. Fallback to .claude/agents/default.md
    """
    base_dir = Path(__file__).resolve().parent.parent

    # 1. Explicit path (highest priority)
    if settings.agent_file_path:
        path = settings.agent_file_path
        if not path.is_absolute():
            path = base_dir / path
        if path.exists():
            log_event("agent_discovery", method="explicit_path", path=str(path))
            return path
        raise FileNotFoundError(f"Explicit agent file not found: {path}")

    # 2. Agent name
    if settings.agent_name:
        path = base_dir / ".claude" / "agents" / f"{settings.agent_name}.md"
        if path.exists():
            log_event("agent_discovery", method="agent_name", path=str(path))
            return path

    # 3. Auto-detect single .md file in .claude/agents/
    agents_dir = base_dir / ".claude" / "agents"
    if agents_dir.exists():
        md_files = list(agents_dir.glob("*.md"))
        # Exclude README.md from auto-detection
        md_files = [f for f in md_files if f.name.lower() != "readme.md"]

        if len(md_files) == 1:
            log_event("agent_discovery", method="auto_detect", path=str(md_files[0]))
            return md_files[0]
        elif len(md_files) > 1:
            raise ValueError(
                f"Multiple agent files found in {agents_dir}. "
                f"Specify AGENT_NAME or AGENT_FILE_PATH. Found: {[f.name for f in md_files]}"
            )

    # 4. Fallback to default.md
    default_path = base_dir / ".claude" / "agents" / "default.md"
    if default_path.exists():
        log_event("agent_discovery", method="fallback_default", path=str(default_path))
        return default_path

    raise FileNotFoundError(
        "No agent file found. Create .claude/agents/default.md or set AGENT_NAME/AGENT_FILE_PATH."
    )


class AgentExecutor:
    """Execute Claude agent with MCP integration."""

    def __init__(self, agent_config: AgentConfig):
        """Initialize executor with agent configuration."""
        self.config = agent_config
        self.model = settings.model_name or agent_config.model  # Env var overrides

    def build_mcp_config(self) -> Dict[str, Any]:
        """Build MCP server configuration from environment."""
        mcp_servers = {}

        # Add Datagen MCP if API key is present
        if settings.datagen_api_key:
            mcp_servers["datagen"] = {
                "type": "http",
                "url": "https://mcp.datagen.dev/mcp",
                "headers": {"Authorization": f"Bearer {settings.datagen_api_key.strip()}"},
            }
            log_event(
                "mcp_config",
                server="datagen",
                url="https://mcp.datagen.dev/mcp",
                authenticated=True,
            )

        # Add more MCP servers here as needed
        # Example:
        # if settings.github_token:
        #     mcp_servers["github"] = {...}

        return mcp_servers

    def _build_options(self) -> ClaudeAgentOptions:
        """Compose Claude agent options."""

        return ClaudeAgentOptions(
            model=self.model,
            system_prompt=self.config.system_prompt,
            permission_mode=settings.permission_mode,
            mcp_servers=self.build_mcp_config(),
            allowed_tools=self.config.allowed_tools if self.config.allowed_tools else None,
        )

    async def stream_execute(self, payload: Dict[str, Any], request_id: str, *, log_success: bool = True):
        """Async generator yielding text chunks for streaming responses."""

        log_event("agent_start", request_id=request_id, agent=self.config.name)
        user_message = self._format_payload(payload)
        opts = self._build_options()

        try:
            async for msg in query(prompt=user_message, options=opts):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            text = block.text
                            log_event(
                                "agent_chunk",
                                request_id=request_id,
                                chunk=text[:500],
                                truncated=len(text) > 500,
                            )
                            yield text
                        elif isinstance(block, ToolUseBlock):
                            log_event(
                                "agent_tool_use",
                                request_id=request_id,
                                tool=block.name,
                                input=block.input,
                            )
                else:
            log_event("agent_event", request_id=request_id, msg_type=type(msg).__name__)

        except Exception as e:
            log_event(
                "agent_error",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
        finally:
            if log_success:
                # result length is calculated by caller when buffering; keep None for streaming
                log_event("agent_success", request_id=request_id, result_length=None)

    async def execute(self, payload: Dict[str, Any], request_id: str) -> str:
        """Execute agent and return concatenated text (non-streaming)."""

        collected_text: list[str] = []
        async for chunk in self.stream_execute(payload, request_id, log_success=False):
            collected_text.append(chunk)

        result = "".join(collected_text)
        log_event("agent_success", request_id=request_id, result_length=len(result))
        return result

    def _format_payload(self, payload: Dict[str, Any]) -> str:
        """Format payload as JSON for the agent."""
        return f"""Here is the input data to process:

```json
{json.dumps(payload, indent=2, ensure_ascii=False)}
```

Process this data according to your system prompt instructions."""


# Load agent configuration at module import (once at startup)
_agent_file = discover_agent_file()
_agent_config = AgentConfig.from_file(_agent_file)
agent_executor = AgentExecutor(_agent_config)

log_event(
    "agent_loaded",
    name=_agent_config.name,
    model=agent_executor.model,
    file=str(_agent_file),
    tools_count=len(_agent_config.allowed_tools),
)
