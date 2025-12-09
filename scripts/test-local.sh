#!/bin/bash
set -e

echo "🧪 Testing Agent Locally"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [[ ! -f .env ]]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Copy .env.example and configure:"
    echo "  cp .env.example .env"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check required variables
if [[ -z "$ANTHROPIC_API_KEY" ]]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set in .env${NC}"
    exit 1
fi

# Start server in background
echo "🚀 Starting server on port 8001..."
PORT=8001 uvicorn app.main:app --reload &
SERVER_PID=$!

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping server..."
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
}

trap cleanup EXIT

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

BASE_URL="http://localhost:8001"

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "GET $BASE_URL/health"
HEALTH_RESPONSE=$(curl -s $BASE_URL/health)
echo "$HEALTH_RESPONSE" | python3 -m json.tool
echo ""

if echo "$HEALTH_RESPONSE" | grep -q '"status": "ok"'; then
    echo -e "${GREEN}✓${NC} Health check passed"
else
    echo -e "${RED}✗${NC} Health check failed"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Agent metadata
echo "Test 2: Agent Metadata"
echo "GET $BASE_URL/agent"
AGENT_RESPONSE=$(curl -s $BASE_URL/agent)
echo "$AGENT_RESPONSE" | python3 -m json.tool
echo ""

if echo "$AGENT_RESPONSE" | grep -q '"name"'; then
    echo -e "${GREEN}✓${NC} Agent metadata retrieved"
else
    echo -e "${RED}✗${NC} Agent metadata failed"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Agent execution
echo "Test 3: Agent Execution"
echo "POST $BASE_URL/run"

PAYLOAD='{"payload": {"text": "Hello, test agent!", "action": "process"}}'
echo "Payload: $PAYLOAD"
echo ""

if [[ -n "$WEBHOOK_SECRET" ]]; then
    RUN_RESPONSE=$(curl -s -X POST $BASE_URL/run \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $WEBHOOK_SECRET" \
        -d "$PAYLOAD")
else
    RUN_RESPONSE=$(curl -s -X POST $BASE_URL/run \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
fi

echo "$RUN_RESPONSE" | python3 -m json.tool
echo ""

if echo "$RUN_RESPONSE" | grep -q '"status": "queued"'; then
    echo -e "${GREEN}✓${NC} Agent execution queued"
else
    echo -e "${RED}✗${NC} Agent execution failed"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# Wait a moment for agent to process
echo "⏳ Waiting for agent to process (5 seconds)..."
sleep 5

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your agent is working! You can now:"
echo "  1. View server logs above to see agent output"
echo "  2. Test with custom payloads:"
echo "     curl -X POST http://localhost:8001/run \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"payload\": {\"your\": \"data\"}}'"
echo "  3. Deploy to Railway:"
echo "     ./scripts/deploy.sh"
echo ""
