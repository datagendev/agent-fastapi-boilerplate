#!/bin/bash
set -e

echo "🚀 Deploying Agent to Railway..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# 1. Pre-flight Checks
# =============================================================================
echo "📋 Running pre-flight checks..."

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Error: Railway CLI not installed${NC}"
    echo ""
    echo "Install Railway CLI with one of these methods:"
    echo "  Homebrew (macOS):  brew install railway"
    echo "  npm (all):         npm i -g @railway/cli"
    echo "  Shell script:      bash <(curl -fsSL cli.new)"
    echo "  Scoop (Windows):   scoop install railway"
    echo ""
    echo "Documentation: https://docs.railway.com/guides/cli"
    exit 1
fi
echo -e "${GREEN}✓${NC} Railway CLI found ($(railway --version))"

# Check if logged in
echo "Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠ Not logged in to Railway${NC}"
    echo "Logging you in now..."
    railway login
    echo -e "${GREEN}✓${NC} Railway login successful"
else
    RAILWAY_USER=$(railway whoami 2>/dev/null || echo "Railway User")
    echo -e "${GREEN}✓${NC} Logged in as: $RAILWAY_USER"
fi

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
    echo -e "${YELLOW}⚠ Warning: ANTHROPIC_API_KEY not set or invalid in .env${NC}"
    echo "Make sure to set it before deploying"
fi

# =============================================================================
# 2. Project Setup
# =============================================================================
echo ""
echo "📡 Setting up Railway project..."

if ! railway status &> /dev/null; then
    echo "No Railway project linked to this directory."
    echo ""
    echo -e "${BLUE}What would you like to do?${NC}"
    echo "  1) Create a new Railway project"
    echo "  2) Link to an existing Railway project"
    echo ""
    read -p "Enter choice (1 or 2): " project_choice

    case $project_choice in
        1)
            echo "Creating new Railway project..."
            railway init
            echo -e "${GREEN}✓${NC} Railway project created"
            ;;
        2)
            echo "Linking to existing Railway project..."
            railway link
            echo -e "${GREEN}✓${NC} Railway project linked"
            ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
else
    PROJECT_INFO=$(railway status 2>/dev/null | grep -i "project" || echo "Railway Project")
    echo -e "${GREEN}✓${NC} Railway project already linked: $PROJECT_INFO"
fi

# =============================================================================
# 3. Environment Variables
# =============================================================================
echo ""
echo "🔧 Setting environment variables..."

# Count variables to set
TOTAL_VARS=$(grep -v '^#' .env | grep -v '^$' | grep -v '...' | grep -v 'your-' | wc -l | tr -d ' ')

if [ "$TOTAL_VARS" -eq 0 ]; then
    echo -e "${YELLOW}⚠ No valid environment variables found in .env${NC}"
    echo "Make sure your .env file has proper values (not placeholders)"
else
    echo "Found $TOTAL_VARS environment variable(s) to set"
    echo ""

    # Read .env and upload to Railway
    # Skip comments, empty lines, and placeholders
    VAR_COUNT=0
    while IFS='=' read -r key value; do
        # Skip empty keys
        [[ -z "$key" ]] && continue

        # Remove quotes from value
        value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

        # Skip if value is a placeholder
        if [[ "$value" == *"..."* ]] || [[ "$value" == "your-"* ]] || [[ -z "$value" ]]; then
            echo -e "${YELLOW}  ⊘${NC} Skipping placeholder: $key"
            continue
        fi

        # Set variable
        echo -e "${GREEN}  ✓${NC} Setting: $key"
        railway variables set "$key=$value" > /dev/null 2>&1 || {
            echo -e "${YELLOW}  ⚠${NC} Warning: Failed to set $key"
        }
        VAR_COUNT=$((VAR_COUNT + 1))
    done < <(grep -v '^#' .env | grep -v '^$')

    echo ""
    echo -e "${GREEN}✓${NC} Set $VAR_COUNT environment variable(s)"
fi

# =============================================================================
# 4. Deployment
# =============================================================================
echo ""
echo "🚢 Deploying to Railway..."
echo ""

# Deploy with detached mode (non-blocking)
railway up --detach

# =============================================================================
# 5. Success Message
# =============================================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment initiated successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📝 Next steps:"
echo ""
echo "  View deployment logs:"
echo -e "    ${BLUE}railway logs${NC}"
echo ""
echo "  Check deployment status:"
echo -e "    ${BLUE}railway status${NC}"
echo ""
echo "  Get your deployment URL:"
echo -e "    ${BLUE}railway domain${NC}"
echo ""
echo "  Open Railway dashboard:"
echo -e "    ${BLUE}railway open${NC}"
echo ""
echo "  Change environment (if needed):"
echo -e "    ${BLUE}railway environment${NC}"
echo ""
echo "🧪 Test your deployment:"
echo "  # First, get your URL:"
echo "  URL=\$(railway domain)"
echo ""
echo "  # Then test the health endpoint:"
echo "  curl \$URL/health"
echo ""
echo "  # Or test the agent:"
echo "  curl -X POST \$URL/run \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"payload\": {\"text\": \"Hello, Railway!\"}}'"
echo ""
echo "📚 Documentation:"
echo "  Railway CLI: https://docs.railway.com/guides/cli"
echo "  This project: README.md"
echo ""
