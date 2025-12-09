#!/bin/bash
set -e

echo "🚀 Deploying Agent to Railway..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Pre-flight checks
echo "📋 Running pre-flight checks..."

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Error: Railway CLI not installed${NC}"
    echo "Install with: npm i -g @railway/cli"
    echo "Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi
echo -e "${GREEN}✓${NC} Railway CLI found"

# Check .env file
if [[ ! -f .env ]]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Copy .env.example and configure your keys:"
    echo "  cp .env.example .env"
    echo "  # Edit .env and set ANTHROPIC_API_KEY"
    exit 1
fi
echo -e "${GREEN}✓${NC} .env file found"

# Validate required environment variables
if ! grep -q "ANTHROPIC_API_KEY=sk-ant-" .env 2>/dev/null; then
    echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not set or invalid in .env${NC}"
    echo "Make sure to set it before deploying"
fi

# 2. Initialize Railway project if needed
echo ""
echo "📡 Checking Railway project..."

if ! railway status &> /dev/null; then
    echo "No Railway project linked. Creating new project..."
    railway init
    echo -e "${GREEN}✓${NC} Railway project created"
else
    echo -e "${GREEN}✓${NC} Railway project already linked"
fi

# 3. Set environment variables
echo ""
echo "🔧 Setting environment variables..."

# Read .env and upload to Railway
# Skip comments and empty lines
grep -v '^#' .env | grep -v '^$' | while IFS='=' read -r key value; do
    # Remove quotes from value
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//')

    # Skip if value is a placeholder
    if [[ "$value" == *"..."* ]] || [[ "$value" == "your-"* ]]; then
        echo -e "${YELLOW}⊘${NC} Skipping placeholder: $key"
        continue
    fi

    # Set variable
    echo "  Setting: $key"
    railway variables set "$key=$value" > /dev/null 2>&1 || true
done

echo -e "${GREEN}✓${NC} Environment variables uploaded"

# 4. Deploy
echo ""
echo "🚢 Deploying to Railway..."
railway up --detach

# 5. Success message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. View logs:    railway logs"
echo "  2. Get URL:      railway domain"
echo "  3. Open dashboard: railway open"
echo ""
echo "Test your deployment:"
echo "  curl https://your-app.railway.app/health"
echo ""
