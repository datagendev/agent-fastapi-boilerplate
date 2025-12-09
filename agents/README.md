# Agent Templates

This directory contains agent configuration files. Each agent is defined in a markdown file with optional YAML frontmatter.

## File Format

### Option 1: agent.md with YAML Frontmatter (Recommended)

```markdown
---
name: my-agent
description: Brief description of what this agent does
tools: mcp__Datagen__executeTool, Read, Write
model: claude-sonnet-4-5
---

# Agent System Prompt

Your detailed instructions go here...
```

### Option 2: Simple prompt.md (Plain Markdown)

If you don't need frontmatter, just write plain markdown:

```markdown
# My Agent

You are a helpful assistant that does X, Y, and Z.

## Instructions

1. Do this
2. Then do that
```

The boilerplate will auto-detect the format.

## Frontmatter Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | No | filename | Agent identifier |
| `description` | No | None | Brief description |
| `tools` | No | DataGen tools | Comma-separated list or array of allowed tools |
| `model` | No | `claude-sonnet-4-5` | Claude model to use |

## Available Tools

### Built-in Tools
- `Read`, `Write`, `Edit` - File operations
- `Bash` - Shell commands
- `Glob`, `Grep` - File searching

### DataGen MCP Tools
If `DATAGEN_API_KEY` is set, you can use:
- `mcp__Datagen__getToolDetails` - Discover available tools
- `mcp__Datagen__executeTool` - Execute any DataGen tool

### Custom Tools
You can add more MCP servers by editing `app/agent.py` → `build_mcp_config()`.

## Writing Effective System Prompts

### 1. Define the Role
```markdown
You are an expert data enrichment agent that finds LinkedIn profiles...
```

### 2. Specify Input Format
```markdown
## Input Format
You will receive:
- `email`: User's email address
- `company`: Optional company name
```

### 3. Provide Step-by-Step Instructions
```markdown
## Process

### Step 1: Search LinkedIn
Use `mcp__Datagen__executeTool` with tool `search_linkedin_person`...

### Step 2: Validate Results
Check if the profile matches...
```

### 4. Include Examples
````markdown
## Example

Input:
```json
{"email": "user@example.com"}
```

Expected output:
```json
{"linkedin_url": "https://linkedin.com/in/...", "confidence": "high"}
```
````

### 5. Handle Edge Cases
```markdown
## Error Handling
- If no results found → return {"status": "not_found"}
- If multiple matches → choose the most recent profile
```

## Agent Selection

The boilerplate discovers agents in this order:

1. **Explicit path**: `AGENT_FILE_PATH=/app/agents/my-agent.md`
2. **Agent name**: `AGENT_NAME=my-agent` → loads `agents/my-agent.md`
3. **Auto-detect**: Single `.md` file in `agents/` directory
4. **Fallback**: `agents/default.md`

## Creating a New Agent

### Method 1: Using the script
```bash
./scripts/init-agent.sh my-agent
```

### Method 2: Manual creation
```bash
cp agents/default.md agents/my-agent.md
# Edit agents/my-agent.md
# Set environment: AGENT_NAME=my-agent
```

## Examples

See the `examples/` directory for complete working examples:
- `examples/enrichment/` - LinkedIn profile enrichment
- `examples/email-drafter/` - Personalized email generation

## Best Practices

1. **Be specific**: Clear, detailed instructions work better than vague ones
2. **Use tools wisely**: Only request tools you actually need
3. **Validate inputs**: Check data before processing
4. **Structure outputs**: Return JSON when possible for easy parsing
5. **Test locally**: Use `./scripts/test-local.sh` before deploying

## Troubleshooting

**Agent not found:**
- Check file exists in `agents/` directory
- Verify `AGENT_NAME` or `AGENT_FILE_PATH` is correct
- Check logs for discovery method used

**Tools not working:**
- Ensure `DATAGEN_API_KEY` is set for MCP tools
- Check `allowed_tools` in frontmatter includes the tool
- Review logs for tool execution errors

**Model not available:**
- Verify model name: `claude-sonnet-4-5`, `claude-opus-4-5`, etc.
- Check `ANTHROPIC_API_KEY` is valid
- Review error logs for specific model errors
