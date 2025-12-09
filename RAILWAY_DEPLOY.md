# Railway Deployment Guide

Complete guide for deploying your Claude Code agent to Railway.

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [First-Time Deployment](#first-time-deployment)
- [Updating Your Deployment](#updating-your-deployment)
- [Environment Management](#environment-management)
- [Monitoring & Debugging](#monitoring--debugging)
- [Troubleshooting](#troubleshooting)

## Installation

Install Railway CLI using one of these methods:

### Homebrew (macOS)
```bash
brew install railway
```

### npm (All Platforms)
```bash
npm i -g @railway/cli
```
Requires Node.js v16+

### Shell Script (macOS, Linux, WSL)
```bash
bash <(curl -fsSL cli.new)
```

### Scoop (Windows)
```bash
scoop install railway
```

### Verify Installation
```bash
railway --version
```

**Official Documentation:** https://docs.railway.com/guides/cli

## Authentication

### Interactive Login
```bash
railway login
```
This opens your browser to complete authentication.

### Browserless Login
For servers or environments without browser access:
```bash
railway login --browserless
```
Follow the pairing code instructions.

### Verify Authentication
```bash
railway whoami
```

## First-Time Deployment

### Option 1: Automated (Recommended)

Use our deployment script:
```bash
./scripts/deploy.sh
```

The script handles everything:
- ✅ Checks Railway CLI installation
- ✅ Authenticates if needed
- ✅ Creates/links project interactively
- ✅ Uploads environment variables from `.env`
- ✅ Deploys your agent

### Option 2: Manual

**Step 1: Prepare your environment**
```bash
# Copy and configure .env
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

**Step 2: Authenticate**
```bash
railway login
```

**Step 3: Create project**
```bash
railway init
```
Follow prompts to name your project and select team.

**Step 4: Set environment variables**

From your `.env` file, manually set each variable:
```bash
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set AGENT_NAME=default
railway variables set DATAGEN_API_KEY=dgn_...  # If using DataGen MCP
```

Or use the automated approach from `scripts/deploy.sh`.

**Step 5: Deploy**
```bash
railway up --detach
```

**Step 6: Get your URL**
```bash
railway domain
```

## Updating Your Deployment

### Quick Update
After making code changes:

```bash
# Option 1: Use the script
./scripts/deploy.sh

# Option 2: Manual
railway up --detach
```

Railway will:
1. Build your Docker image
2. Deploy the new version
3. Automatically handle zero-downtime deployment

### Update Environment Variables

```bash
# Update a single variable
railway variables set AGENT_NAME=new-agent

# Delete a variable
railway variables delete OLD_VAR

# List all variables
railway variables
```

After updating variables, redeploy:
```bash
railway up --detach
```

## Environment Management

Railway supports multiple environments (production, staging, etc.).

### List Environments
```bash
railway environment
```

### Switch Environment
```bash
railway environment
# Follow prompts to select environment
```

### Deploy to Specific Environment
```bash
# First, switch to the environment
railway environment

# Then deploy
railway up --detach
```

### Environment-Specific Variables

Each environment has its own variables. Switch to the environment first, then set variables:
```bash
# Switch to staging
railway environment
# Select "staging"

# Set staging-specific variables
railway variables set ANTHROPIC_API_KEY=sk-ant-staging-key

# Deploy to staging
railway up --detach
```

## Monitoring & Debugging

### View Logs

**Stream logs in real-time:**
```bash
railway logs --follow
```

**View recent logs:**
```bash
railway logs
```

**Filter logs by time:**
```bash
railway logs --since 1h    # Last hour
railway logs --since 30m   # Last 30 minutes
```

### Check Status
```bash
railway status
```

### SSH into Container

Access your running container:
```bash
railway ssh
```

Once inside, you can:
```bash
# Check agent file
cat .claude/agents/default.md

# View environment variables
env | grep ANTHROPIC

# Check Python version
python --version

# Test imports
python -c "from app.main import app; print('App loads OK')"
```

**Note:** Railway uses WebSocket-based SSH, not standard SSH protocol.

### Get Deployment URL
```bash
railway domain
```

### Open Dashboard
```bash
railway open
```

## Troubleshooting

### Build Fails

**Check build logs:**
```bash
railway logs
```

**Common issues:**
- Missing dependencies in `requirements.txt`
- Incorrect Python version in `runtime.txt`
- Docker build errors

**Solution:**
1. Test Docker build locally:
   ```bash
   docker build -t test-agent .
   ```
2. Fix any errors
3. Redeploy:
   ```bash
   railway up --detach
   ```

### Agent Not Found Error

**Error message:**
```
FileNotFoundError: No agent file found
```

**Check:**
1. Verify agent file exists:
   ```bash
   railway ssh
   ls .claude/agents/
   ```

2. Check `AGENT_NAME` environment variable:
   ```bash
   railway variables | grep AGENT_NAME
   ```

3. Ensure file is included in Docker build (not in `.dockerignore`)

### Permission Denied Errors

**Error message:**
```
EACCES: permission denied
```

**Cause:** Running as root user (Claude Agent SDK requires non-root)

**Solution:**
Our Dockerfile already handles this. If you modified the Dockerfile, ensure:
```dockerfile
USER appuser  # Must be non-root
```

### MCP Tools Not Working

**Check:**
1. `DATAGEN_API_KEY` is set:
   ```bash
   railway variables | grep DATAGEN_API_KEY
   ```

2. API key is valid (not a placeholder)

3. Tools are listed in agent.md `allowed_tools`

4. View logs for MCP connection errors:
   ```bash
   railway logs --follow
   ```

### Deployment Stuck

If deployment hangs:

1. **Cancel and retry:**
   ```bash
   # Cancel with Ctrl+C
   railway up --detach
   ```

2. **Check Railway status:**
   ```bash
   railway status
   ```

3. **View logs for errors:**
   ```bash
   railway logs
   ```

### Environment Variables Not Updating

After setting variables, you **must redeploy**:
```bash
railway variables set NEW_VAR=value
railway up --detach  # Required!
```

Variables are injected at deployment time, not runtime.

## Advanced Usage

### Using Railway Tokens (CI/CD)

For automated deployments (GitHub Actions, etc.):

1. **Generate project token:**
   - Go to Railway dashboard
   - Project Settings → Tokens
   - Create new token

2. **Set in CI/CD:**
   ```bash
   export RAILWAY_TOKEN=your-project-token
   ```

3. **Deploy:**
   ```bash
   railway up --detach
   ```

**Documentation:** https://docs.railway.com/guides/cli#railway-environment-variables

### Multiple Services

If you add additional services (databases, Redis, etc.):

```bash
# Add a service (e.g., PostgreSQL)
railway add

# List services
railway status

# Link services (automatic in same project)
# Services can reference each other via private networking
```

### Custom Domains

```bash
# Add a custom domain
railway domain add example.com

# List domains
railway domain

# Remove domain
railway domain remove example.com
```

## Best Practices

1. **Use `.env` files locally**
   - Keep `.env` in `.gitignore`
   - Use `scripts/deploy.sh` to sync variables

2. **Test locally first**
   ```bash
   ./scripts/test-local.sh
   ```

3. **Use `--detach` for deployments**
   - Faster deploys
   - Non-blocking terminal

4. **Monitor logs after deployment**
   ```bash
   railway logs --follow
   ```

5. **Use environments for staging/production**
   - Separate configurations
   - Test changes in staging first

## Quick Reference

| Task | Command |
|------|---------|
| Deploy | `railway up --detach` |
| View logs | `railway logs --follow` |
| Get URL | `railway domain` |
| SSH into container | `railway ssh` |
| Set variable | `railway variables set KEY=value` |
| Switch environment | `railway environment` |
| Check status | `railway status` |
| Open dashboard | `railway open` |

## Getting Help

- **Railway Documentation:** https://docs.railway.com
- **Railway CLI Guide:** https://docs.railway.com/guides/cli
- **Railway Discord:** https://discord.gg/railway
- **This Project:** README.md

---

**Ready to deploy?** Run `./scripts/deploy.sh` to get started! 🚀
