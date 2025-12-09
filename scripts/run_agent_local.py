"""Minimal standalone runner for Claude Agent SDK with local directory access.

Usage:
    python scripts/run_agent_local.py "list the files under scripts/"
    python scripts/run_agent_local.py --cwd /path/to/project "summarize README.md"

Environment:
    Requires ANTHROPIC_API_KEY to be set.
"""

import argparse
from pathlib import Path
import sys

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    query,
)


def _print_block(block) -> None:
    """Pretty-print a single content block."""
    if isinstance(block, TextBlock):
        print(block.text)
    elif isinstance(block, ToolUseBlock):
        print(f"[tool:{block.name}] args={block.input}")
    elif isinstance(block, ToolResultBlock):
        output = getattr(block, "output", None) or getattr(block, "content", None)
        print(f"[tool-result:{block.name}] {output}")
    else:
        print(block)


async def run(prompt: str, cwd: Path) -> None:
    """Stream a single prompt through the Agent SDK with local FS + bash tools."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="bypassPermissions",  # auto-approve all tool calls
        cwd=str(cwd),
        setting_sources=None,  # keep it standalone; ignore project/user settings
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                _print_block(block)
        else:
            # Tool and system messages are rare; fall back to repr
            print(message)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run a one-off Claude agent task locally.")
    parser.add_argument("prompt", help="Natural language instruction for the agent.")
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="Working directory Claude can read/write/execute (default: current directory).",
    )
    args = parser.parse_args(argv)

    try:
        anyio.run(run, args.prompt, args.cwd)
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
