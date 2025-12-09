#!/bin/bash
set -e

# Default agent name
AGENT_NAME=${1:-my-agent}

echo "🤖 Creating new agent: $AGENT_NAME"
echo ""

# Create agent file
AGENT_FILE=".claude/agents/${AGENT_NAME}.md"

if [[ -f "$AGENT_FILE" ]]; then
    echo "❌ Agent already exists: $AGENT_FILE"
    echo "Choose a different name or edit the existing file"
    exit 1
fi

# Create agent.md with template
cat > "$AGENT_FILE" <<'EOF'
---
name: AGENT_NAME_PLACEHOLDER
description: A helpful agent that processes data
tools: mcp__Datagen__getToolDetails, mcp__Datagen__executeTool
model: claude-sonnet-4-5
---

# AGENT_NAME_PLACEHOLDER

You are a helpful AI assistant that processes data according to specific instructions.

## Your Role

Describe what this agent does and what it's responsible for.

## Input Format

Specify what input data the agent expects:
- `field1`: Description
- `field2`: Description

## Process

### Step 1: First Task
Explain what to do first...

### Step 2: Second Task
Explain what to do next...

## Output Format

Define what the agent should return:
```json
{
  "result": "...",
  "status": "success"
}
```

## Error Handling

Describe how to handle errors:
- If X happens → do Y
- If Z happens → do W

## Examples

Provide concrete examples of input/output.
EOF

# Replace placeholder with actual agent name
sed -i.bak "s/AGENT_NAME_PLACEHOLDER/$AGENT_NAME/g" "$AGENT_FILE"
rm "${AGENT_FILE}.bak"

echo "✅ Created agent file: $AGENT_FILE"
echo ""
echo "Next steps:"
echo "  1. Edit the agent file: $AGENT_FILE"
echo "  2. Customize the system prompt for your use case"
echo "  3. Test locally:"
echo "       AGENT_NAME=$AGENT_NAME uvicorn app.main:app --reload"
echo "  4. Or use the test script:"
echo "       AGENT_NAME=$AGENT_NAME ./scripts/test-local.sh"
echo ""
echo "📝 Agent template created! Edit $AGENT_FILE to customize."
