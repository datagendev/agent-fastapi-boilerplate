# Agent FastAPI Boilerplate

A production-ready FastAPI boilerplate for deploying Claude Code agents to Railway. Drop your `agent.md`, set 3 env vars, and deploy in under 10 minutes.

## Features

- 🚀 **One-command deployment** to Railway
- 📝 **Supports both formats**: agent.md (with YAML frontmatter) and prompt.md (plain markdown)
- 🔧 **Auto-discovery**: Automatically finds your agent file
- 🔐 **Production-ready**: API key auth, structured logging, error handling
- 🛠️ **MCP Integration**: Built-in DataGen MCP support
- 📊 **Background processing**: Non-blocking agent execution
- 🐳 **Docker-ready**: Non-root user setup for Claude Agent SDK
- ✅ **Testing included**: Local testing script

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

```bash
# 1. Clone and setup
git clone <this-repo> my-agent && cd my-agent
cp .env.example .env
# Edit .env: Add ANTHROPIC_API_KEY

# 2. Add your agent
cp examples/enrichment/agent.md agents/my-agent.md
# Or: ./scripts/init-agent.sh my-agent

# 3. Test locally
./scripts/test-local.sh

# 4. Deploy to Railway
./scripts/deploy.sh
```

## Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Agent Format](#agent-format)
- [API Endpoints](#api-endpoints)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [Examples](#examples)
- [Extending the Boilerplate](#extending-the-boilerplate)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Architecture

### Directory Structure

```
agent-fastapi-boilerplate/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration management
│   ├── agent.py         # Agent loading & execution
│   └── models.py        # Pydantic schemas
├── agents/
│   ├── default.md       # Default agent
│   └── README.md        # Agent documentation
├── examples/
│   ├── enrichment/      # LinkedIn enrichment example
│   └── email-drafter/   # Email drafting example
├── scripts/
│   ├── deploy.sh        # Deploy to Railway
│   ├── init-agent.sh    # Create new agent
│   └── test-local.sh    # Local testing
├── Dockerfile           # Non-root user setup
├── railway.json         # Railway configuration
└── requirements.txt     # Python dependencies
```

### How It Works

1. **Agent Discovery**: Automatically finds your agent.md file
2. **Configuration**: Loads settings from environment variables
3. **Execution**: Accepts JSON payloads via `/run` endpoint
4. **Background Processing**: Executes agent asynchronously
5. **MCP Integration**: Auto-configures DataGen MCP if API key present

## Installation

### Prerequisites

- Python 3.13+
- Railway CLI (for deployment)
- Anthropic API key

### Setup

```bash
# Clone the repository
git clone <repo-url> my-agent-project
cd my-agent-project

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your ANTHROPIC_API_KEY
nano .env
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-api03-...` |

#### Agent Selection (choose one)

| Variable | Description | Example |
|----------|-------------|---------|
| `AGENT_NAME` | Agent name (loads `agents/{AGENT_NAME}.md`) | `default` |
| `AGENT_FILE_PATH` | Explicit path to agent file | `/app/agents/my-agent.md` |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DATAGEN_API_KEY` | DataGen MCP API key | None |
| `WEBHOOK_SECRET` | API key for `/run` endpoint auth | None |
| `MODEL_NAME` | Override agent.md model | `claude-sonnet-4-5` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PORT` | Server port | `8000` |
| `PERMISSION_MODE` | Agent SDK permission mode | `bypassPermissions` |

### Agent Discovery

The boilerplate discovers agents in this order:

1. **Explicit path**: `AGENT_FILE_PATH=/app/agents/my-agent.md`
2. **Agent name**: `AGENT_NAME=enrichment` → loads `agents/enrichment.md`
3. **Auto-detect**: Single `.md` file in `agents/` directory (excludes README.md)
4. **Fallback**: `agents/default.md`

## Agent Format

### Option 1: agent.md with YAML Frontmatter (Recommended)

```markdown
---
name: my-agent
description: Brief description of what this agent does
tools: mcp__Datagen__executeTool, Read, Write
model: claude-sonnet-4-5
---

# System Prompt

Detailed instructions for the agent...
```

### Option 2: Simple prompt.md

Plain markdown without frontmatter:

```markdown
# My Agent

You are a helpful assistant that processes data...
```

See [agents/README.md](agents/README.md) for detailed documentation on writing agents.

## API Endpoints

### `POST /run`

Execute agent with JSON payload.

**Request:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret" \  # If WEBHOOK_SECRET is set
  -d '{"payload": {"email": "user@example.com"}}'
```

**Response:**
```json
{
  "status": "queued",
  "request_id": "abc-123-def",
  "message": "Agent 'default' is processing your request"
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "agent_name": "default",
  "model": "claude-sonnet-4-5",
  "ready": true
}
```

### `GET /agent`

Get agent metadata.

**Response:**
```json
{
  "name": "default",
  "description": "A helpful AI assistant",
  "tools": ["mcp__Datagen__executeTool"],
  "model": "claude-sonnet-4-5"
}
```

## Local Development

### Run Server

```bash
# Load environment variables
source .env

# Start server with auto-reload
uvicorn app.main:app --reload --port 8000
```

### Test Locally

```bash
# Use the test script
./scripts/test-local.sh

# Or test manually
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "Hello world"}}'
```

### Create New Agent

```bash
# Using script (recommended)
./scripts/init-agent.sh my-new-agent

# Or manually
cp agents/default.md agents/my-new-agent.md
# Edit agents/my-new-agent.md
```

## Deployment

### Deploy to Railway

```bash
# One-command deployment
./scripts/deploy.sh
```

This script will:
1. Check Railway CLI is installed
2. Validate `.env` file exists
3. Initialize Railway project (if needed)
4. Upload environment variables
5. Deploy using Dockerfile

### Manual Deployment

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link or create project
railway init

# Set environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set AGENT_NAME=default

# Deploy
railway up
```

### Post-Deployment

```bash
# View logs
railway logs --follow

# Get deployment URL
railway domain

# Open Railway dashboard
railway open
```

## Examples

### Example 1: Enrichment Agent

See [examples/enrichment/](examples/enrichment/)

Finds LinkedIn profiles from signup emails.

```bash
cp examples/enrichment/agent.md agents/enrichment.md
cp examples/enrichment/.env.example .env
# Edit .env: Add ANTHROPIC_API_KEY and DATAGEN_API_KEY
AGENT_NAME=enrichment ./scripts/test-local.sh
```

### Example 2: Email Drafter

See [examples/email-drafter/](examples/email-drafter/)

Drafts personalized re-engagement emails.

```bash
cp examples/email-drafter/agent.md agents/email-drafter.md
cp examples/email-drafter/.env.example .env
# Edit .env: Add ANTHROPIC_API_KEY and DATAGEN_API_KEY
AGENT_NAME=email-drafter ./scripts/test-local.sh
```

## Extending the Boilerplate

### Add Custom MCP Servers

Edit `app/agent.py` → `AgentExecutor.build_mcp_config()`:

```python
def build_mcp_config(self) -> Dict[str, Any]:
    mcp_servers = {}

    # Existing: DataGen
    if settings.datagen_api_key:
        mcp_servers["datagen"] = {...}

    # Add new: GitHub MCP
    if os.getenv("GITHUB_TOKEN"):
        mcp_servers["github"] = {
            "type": "sse",
            "url": "https://github-mcp.example.com/sse",
            "headers": {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
        }

    return mcp_servers
```

### Add Custom Endpoints

Edit `app/main.py`:

```python
@app.post("/custom-endpoint")
async def custom_handler(request: CustomRequest):
    # Your custom logic
    return {"result": "success"}
```

### Add Custom Middleware

Edit `app/main.py`:

```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Pre-processing
    response = await call_next(request)
    # Post-processing
    return response
```

## Troubleshooting

### Agent file not found

**Error:** `FileNotFoundError: No agent file found`

**Solution:**
- Ensure `agents/default.md` exists or set `AGENT_NAME`
- Check file path is correct
- Review logs for discovery method used

### ANTHROPIC_API_KEY not set

**Error:** `ValueError: ANTHROPIC_API_KEY is required`

**Solution:**
- Add `ANTHROPIC_API_KEY=sk-ant-...` to `.env`
- Or set as environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`

### Permission denied errors

**Error:** `EACCES: permission denied`

**Solution:**
- Ensure Dockerfile creates non-root user (included by default)
- Check `permission_mode` is set to `bypassPermissions`
- Verify home directory ownership in Docker: `chown -R appuser:appuser /home/appuser`

### MCP tools not working

**Error:** Tools not executing

**Solution:**
- Set `DATAGEN_API_KEY` in `.env`
- Add tools to `allowed_tools` in agent.md frontmatter
- Check MCP server URL in logs
- Verify API key is valid

### Railway deployment fails

**Error:** Build or runtime errors

**Solution:**
- Check Railway logs: `railway logs`
- Ensure all environment variables are set in Railway dashboard
- Verify Dockerfile builds locally: `docker build -t test .`
- Check runtime.txt has `python-3.13`

## Project Structure

```
agent-fastapi-boilerplate/
├── app/                      # Application code
│   ├── __init__.py
│   ├── main.py              # FastAPI app (endpoints, middleware)
│   ├── config.py            # Configuration (env vars)
│   ├── agent.py             # Agent loading & execution
│   └── models.py            # Pydantic schemas
├── agents/                   # Agent definitions
│   ├── default.md           # Default agent
│   └── README.md            # Agent documentation
├── examples/                 # Example agents
│   ├── enrichment/
│   └── email-drafter/
├── scripts/                  # Deployment scripts
│   ├── deploy.sh            # Deploy to Railway
│   ├── init-agent.sh        # Create new agent
│   └── test-local.sh        # Local testing
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── Dockerfile               # Docker configuration
├── Procfile                 # Process file for Railway
├── railway.json             # Railway configuration
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version
├── README.md                # This file
└── QUICKSTART.md            # 5-minute setup guide
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `./scripts/test-local.sh`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **Documentation**: See [agents/README.md](agents/README.md) for agent writing guide
- **Examples**: Check [examples/](examples/) for working examples
- **Issues**: Report bugs or request features via GitHub Issues

## Credits

Built for deploying Claude Code agents with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Railway](https://railway.app/)
