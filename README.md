# Agent FastAPI Boilerplate

A production-ready FastAPI boilerplate for deploying Claude Code agents to Railway. Drop your `agent.md`, set 3 env vars, and deploy in under 10 minutes.

## Features

- 🚀 **One-command deployment** to Railway
- 📝 **Supports both formats**: agent.md (with YAML frontmatter) and prompt.md (plain markdown)
- 🔧 **Auto-discovery**: Automatically finds your agent file
- 🔐 **Production-ready**: API key auth, structured logging, error handling, health checks
- 🛠️ **MCP Integration**: Built-in DataGen MCP support
- 📊 **Background processing**: Non-blocking agent execution with streaming support
- 🐳 **Docker-ready**: Non-root user setup, optimized builds with .dockerignore
- 🌐 **CORS support**: Configurable CORS for frontend integrations
- ✅ **Testing included**: Local testing script with comprehensive health checks

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

```bash
# 1. Clone and setup
git clone https://github.com/datagendev/agent-fastapi-boilerplate my-agent && cd my-agent
cp .env.example .env
# Edit .env: Add ANTHROPIC_API_KEY

# 2. Add your agent
cp examples/email-drafter/agent.md .claude/agents/my-agent.md
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

### How It Works

1. **Agent Discovery**: Automatically finds your agent.md file
2. **Configuration**: Loads settings from environment variables
3. **Execution**: Accepts JSON payloads via `/run` endpoint
4. **Background Processing**: Executes agent asynchronously
5. **MCP Integration**: Auto-configures DataGen MCP if API key present

### Directory Structure

```
agent-fastapi-boilerplate/
├── app/                      # Application code
│   ├── __init__.py
│   ├── main.py              # FastAPI app (endpoints, middleware)
│   ├── config.py            # Configuration (env vars)
│   ├── agent.py             # Agent loading & execution
│   └── models.py            # Pydantic schemas
├── .claude/agents/          # Agent definitions
│   ├── default.md           # Default agent
│   └── README.md            # Agent documentation
├── examples/                # Example agents
│   ├── poem-email-drafter/  # Simple Gmail poem drafter
│   └── email-drafter/       # Email drafting example
├── scripts/                 # Deployment scripts
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
├── QUICKSTART.md            # 5-minute setup guide
└── RAILWAY_DEPLOY.md        # Railway deployment guide
```

## Installation

### Prerequisites

- Python 3.13+
- Railway CLI (for deployment) - [Installation guide](https://docs.railway.com/guides/cli)
- Anthropic API key - [Get one here](https://console.anthropic.com/settings/keys)
- Claude Code desktop app (for local MCP testing) - [Installation](https://claude.ai/install.sh)
- DataGen API key (optional, for DataGen MCP tools) - [Get key](https://datagen.dev/account?tab=api)

> **Note:** See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions including MCP server configuration.

### Setup

```bash
# Clone the repository
git clone https://github.com/datagendev/agent-fastapi-boilerplate my-agent-project
cd my-agent-project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

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
| `AGENT_NAME` | Agent name (loads `.claude/agents/{AGENT_NAME}.md`) | `default` |
| `AGENT_FILE_PATH` | Explicit path to agent file | `/app/.claude/agents/my-agent.md` |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DATAGEN_API_KEY` | DataGen MCP API key | None |
| `WEBHOOK_SECRET` | API key for `/run` endpoint auth | None |
| `MODEL_NAME` | Override agent.md model | `claude-sonnet-4-5` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PORT` | Server port | `8000` |
| `PERMISSION_MODE` | Agent SDK permission mode | `bypassPermissions` |
| `CORS_ENABLED` | Enable CORS for frontend integrations | `false` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |

### Agent Discovery

The boilerplate discovers agents in this order:

1. **Explicit path**: `AGENT_FILE_PATH=/app/.claude/agents/my-agent.md`
2. **Agent name**: `AGENT_NAME=email-drafter` → loads `.claude/agents/email-drafter.md`
3. **Auto-detect**: Single `.md` file in `.claude/agents/` directory (excludes README.md)
4. **Fallback**: `.claude/agents/default.md`

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

See [.claude/agents/README.md](.claude/agents/README.md) for detailed documentation on writing agents.

## API Endpoints

### `POST /run`

Queue agent execution in the background.

**Request:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret" \  # If WEBHOOK_SECRET is set
  -d '{"payload": {"email": "user@example.com"}}'
```

**Response (queued):**
```json
{
  "status": "queued",
  "request_id": "abc-123-def",
  "message": "Agent 'default' is processing your request"
}
```

### `POST /run/sync`

Waits for completion and returns the full text result.

```bash
curl -X POST http://localhost:8000/run/sync \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "Hello"}}'
```

**Response (completed):**
```json
{
  "status": "completed",
  "request_id": "abc-123-def",
  "message": "Agent 'default' completed",
  "result": "...full agent output..."
}
```

### `POST /run/stream`

Streams results via Server-Sent Events (SSE).

```bash
curl -N -X POST http://localhost:8000/run/stream \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "stream me"}}'
```

Each chunk arrives as `data: <text>\n\n`; completion emits `event: done`.

### `GET /health`

Health check endpoint with agent status.

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
# Activate virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

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
cp .claude/agents/default.md .claude/agents/my-new-agent.md
# Edit .claude/agents/my-new-agent.md
```

## Deployment

> 📘 **Complete Railway Guide:** See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for detailed deployment instructions, troubleshooting, and best practices.

### Prerequisites

- Railway CLI installed - see [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md#installation) for installation instructions

### Quick Deploy

```bash
# One-command deployment (recommended)
./scripts/deploy.sh
```

The script will:
1. ✅ Check Railway CLI is installed and authenticated
2. ✅ Validate `.env` file exists with required variables
3. ✅ Authenticate with Railway (if needed)
4. ✅ Create new project OR link to existing project
5. ✅ Upload environment variables from `.env`
6. ✅ Deploy using Dockerfile
7. ✅ Provide next steps and testing commands

### Manual Deployment

If you prefer manual control:

```bash
# 1. Authenticate
railway login

# 2. Create new project
railway init
# Or link to existing project
railway link

# 3. Set environment variables (option A: one by one)
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set AGENT_NAME=default
railway variables set DATAGEN_API_KEY=dgn_...

# Or (option B: from .env file)
# See scripts/deploy.sh for automated approach

# 4. Deploy
railway up --detach

# 5. Get deployment URL
railway domain
```

### Railway Environments

Railway supports multiple environments (production, staging, etc.):

```bash
# List environments
railway environment

# Switch environment
railway environment
# Follow prompts to select environment

# Deploy to specific environment
railway up --detach
```

### Post-Deployment

```bash
# View logs
railway logs --follow

# Check deployment status
railway status

# Get deployment URL
railway domain

# Open Railway dashboard
railway open

# SSH into your container (for debugging)
railway ssh
```

### Railway CLI Reference

Common commands you'll use:

| Command | Description |
|---------|-------------|
| `railway login` | Authenticate with Railway |
| `railway whoami` | Check current user |
| `railway init` | Create new project |
| `railway link` | Link to existing project |
| `railway up` | Deploy your code |
| `railway up --detach` | Deploy without blocking |
| `railway status` | Check project status |
| `railway logs` | View deployment logs |
| `railway logs --follow` | Stream logs in real-time |
| `railway domain` | Get deployment URL |
| `railway open` | Open Railway dashboard |
| `railway environment` | Switch environments |
| `railway variables` | List environment variables |
| `railway variables set KEY=value` | Set environment variable |
| `railway ssh` | SSH into running container |
| `railway run <cmd>` | Run command with Railway env vars |
| `railway shell` | Open shell with Railway env vars |

**Documentation:** https://docs.railway.com/guides/cli

## Examples

### Example 1: Poem Email Drafter (Simple Gmail Agent)

See [examples/poem-email-drafter/](examples/poem-email-drafter/)

Creates Gmail draft emails with poems about any topic. Perfect for learning the basics!

**What it does:**
- Takes webhook with `{topic: "sunset"}`
- Composes creative poem (8-16 lines)
- Creates Gmail draft via DataGen MCP

**Setup:**
```bash
cp examples/poem-email-drafter/agent.md .claude/agents/poem-email-drafter.md
cp .env.example .env
# Edit .env: Add ANTHROPIC_API_KEY and DATAGEN_API_KEY

# Test with poem-email-drafter agent
AGENT_NAME=poem-email-drafter ./scripts/test-local.sh
```

**Usage:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"payload": {"topic": "winter morning"}}'
```

### Example 2: Email Drafter

See [examples/email-drafter/](examples/email-drafter/)

Drafts personalized re-engagement emails.

**Prerequisite:** Add the DataGen MCP server in Claude Code and set `DATAGEN_API_KEY`. Without this, the agent cannot call the database tools it needs.

Add DataGen MCP in Claude Code:
```bash
# Use your API key from https://datagen.dev/account?tab=api
# (Should match DATAGEN_API_KEY in your .env file)
export DATAGEN_API_KEY=your-datagen-key

# Register the MCP server
claude mcp add --transport http datagen https://mcp.datagen.dev/mcp --header "x-api-key: $DATAGEN_API_KEY"

# Verify it shows up
claude mcp list
```

You should see DataGen tools available (the specific tools depend on which services you've connected in your DataGen account).

**UI Alternative:** Claude Code Settings → Developer → MCP Servers → Add MCP Server (match the values above).
![Add DataGen MCP to Claude Code](instruction/add-mcp.png)

```bash
cp examples/email-drafter/agent.md .claude/agents/email-drafter.md
cp .env.example .env
# Edit .env: Add ANTHROPIC_API_KEY and DATAGEN_API_KEY

# Test with email-drafter agent
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
- Ensure `.claude/agents/default.md` exists or set `AGENT_NAME`
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

- **Documentation**: See [.claude/agents/README.md](.claude/agents/README.md) for agent writing guide
- **Examples**: Check [examples/](examples/) for working examples
- **Issues**: Report bugs or request features via GitHub Issues

## Credits

Built for deploying Claude Code agents with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Railway](https://railway.app/)
