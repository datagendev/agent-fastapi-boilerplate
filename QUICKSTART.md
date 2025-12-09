# Quick Start Guide

Get from clone to deployed in **5 minutes**.

## Prerequisites

- Python 3.13+
- Anthropic API key ([Get one here](https://console.anthropic.com/settings/keys))
- Railway CLI (optional, for deployment)

## Step 1: Clone and Setup (1 min)

```bash
# Clone the repository (replace with your repo URL)
git clone <repo-url> my-agent-project
cd my-agent-project

# Create environment file
cp .env.example .env
```

**Edit `.env` and add your API key:**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
AGENT_NAME=default
```

## Step 2: Choose or Create an Agent (1 min)

### Option A: Use an Example Agent

```bash
# Use the enrichment agent example
cp examples/enrichment/agent.md agents/enrichment.md
```

Then update `.env`:
```bash
AGENT_NAME=enrichment
DATAGEN_API_KEY=dgn_your-key-here  # Required for enrichment agent
```

### Option B: Use the Default Agent

The default agent is already set up. No changes needed!

### Option C: Create a Custom Agent

```bash
./scripts/init-agent.sh my-custom-agent
# Edit agents/my-custom-agent.md
```

Then update `.env`:
```bash
AGENT_NAME=my-custom-agent
```

## Step 3: Test Locally (1 min)

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
./scripts/test-local.sh
```

You should see:
```
✓ Health check passed
✓ Agent metadata retrieved
✓ Agent execution queued
✅ All tests passed!
```

## Step 4: Deploy to Railway (2 min)

```bash
# Install Railway CLI (if not already installed)
npm i -g @railway/cli

# Deploy
./scripts/deploy.sh
```

The script will:
1. Check prerequisites
2. Create/link Railway project
3. Upload environment variables from `.env`
4. Deploy your agent

## Step 5: Test Your Deployed Agent

```bash
# Get your deployment URL
railway domain

# Test the health endpoint
curl https://your-app.railway.app/health

# Test agent execution
curl -X POST https://your-app.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "Hello, deployed agent!"}}'
```

## That's It! 🎉

Your agent is now deployed and ready to use.

## Next Steps

### Monitor Your Agent

```bash
# View logs
railway logs --follow

# Open Railway dashboard
railway open
```

### Customize Your Agent

1. Edit your agent file: `agents/your-agent.md`
2. Test locally: `./scripts/test-local.sh`
3. Redeploy: `./scripts/deploy.sh`

### Add Webhook Security

Update `.env`:
```bash
WEBHOOK_SECRET=your-random-secret-key
```

Generate a secure secret:
```bash
openssl rand -hex 32
```

Then redeploy:
```bash
./scripts/deploy.sh
```

Now all requests to `/run` must include the header:
```bash
-H "X-API-Key: your-random-secret-key"
```

### Use a Different Model

Update `.env`:
```bash
MODEL_NAME=claude-opus-4-5
```

Available models:
- `claude-sonnet-4-5` (default, balanced)
- `claude-opus-4-5` (most capable)
- `claude-haiku-4` (fastest, cheapest)

## Troubleshooting

### "ANTHROPIC_API_KEY is required"

Make sure you've added your API key to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### "Agent file not found"

Check that your agent file exists:
```bash
ls agents/
```

Make sure `AGENT_NAME` in `.env` matches the filename (without `.md`):
```bash
AGENT_NAME=my-agent  # Loads agents/my-agent.md
```

### "Railway CLI not found"

Install Railway CLI:
```bash
npm i -g @railway/cli
```

Or visit: https://docs.railway.app/develop/cli

### Tests fail locally

1. Check `.env` has valid `ANTHROPIC_API_KEY`
2. Ensure Python dependencies are installed: `pip install -r requirements.txt`
3. Check logs for specific errors

## Common Use Cases

### Process Email Signups

```bash
curl -X POST https://your-app.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{"payload": {"email": "user@example.com", "source": "homepage"}}'
```

### Analyze Text

```bash
curl -X POST https://your-app.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "Your text here", "action": "analyze"}}'
```

### Custom Workflow

Create an agent with your specific instructions:
```bash
./scripts/init-agent.sh my-workflow
# Edit agents/my-workflow.md
AGENT_NAME=my-workflow ./scripts/test-local.sh
```

## Full Documentation

For detailed documentation, see [README.md](README.md).

For agent writing guide, see [agents/README.md](agents/README.md).

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review the [examples/](examples/) directory for working examples
- Open an issue on GitHub for bugs or feature requests

---

**You're all set!** Happy building! 🚀
