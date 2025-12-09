# Poem Email Drafter Example

A simple agent that creates Gmail draft emails with poems about any topic.

## What It Does

When you send a webhook with a topic, this agent:
1. Composes a creative poem about the topic (8-16 lines)
2. Creates a draft email in Gmail with the poem
3. Returns confirmation with the draft ID

## Requirements

- Anthropic API key
- DataGen API key with Gmail MCP connected
- Gmail account connected to DataGen

## Setup

1. **Copy the agent:**
   ```bash
   cp examples/poem-email-drafter/agent.md .claude/agents/poem-email-drafter.md
   ```

2. **Configure environment:**
   ```bash
   cp examples/poem-email-drafter/.env.example .env
   # Edit .env and add:
   # - ANTHROPIC_API_KEY
   # - DATAGEN_API_KEY
   ```

3. **Test locally:**
   ```bash
   AGENT_NAME=poem-email-drafter ./scripts/test-local.sh
   ```

4. **Deploy to Railway:**
   ```bash
   # Make sure .env has correct values
   ./scripts/deploy.sh
   ```

## Usage

### Test Locally

```bash
# Start the server
AGENT_NAME=poem-email-drafter uvicorn app.main:app --reload

# In another terminal, send a webhook:
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "topic": "winter morning"
    }
  }'
```

### Production (After Deployment)

```bash
# Get your Railway URL
URL=$(railway domain)

# Send webhook
curl -X POST $URL/run \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "topic": "ocean waves"
    }
  }'
```

## Payload Format

### Required Fields

```json
{
  "payload": {
    "topic": "your topic here"
  }
}
```

### Optional Fields

```json
{
  "payload": {
    "topic": "sunset",
    "to": "friend@example.com",
    "subject": "A Sunset Poem for You"
  }
}
```

## Example Topics

Try these topics:
- `"coffee on a rainy day"`
- `"first day of spring"`
- `"city lights at night"`
- `"childhood memories"`
- `"mountain adventure"`
- `"digital age"`
- `"friendship"`
- `"innovation"`

## Expected Output

The agent will return:
```json
{
  "status": "success",
  "topic": "winter morning",
  "draft_id": "r1234567890abcdef",
  "subject": "A Poem About Winter Morning",
  "recipient": "recipient@example.com",
  "poem_preview": "Frost kisses the window pane...",
  "message": "Draft created successfully! Check your Gmail drafts."
}
```

## Checking Your Drafts

After the agent runs, check your Gmail drafts:
1. Go to https://mail.google.com
2. Click "Drafts" in the left sidebar
3. Find the draft with your poem

## Troubleshooting

### "Gmail MCP not available"

Make sure:
- `DATAGEN_API_KEY` is set in `.env`
- Your Gmail account is connected to DataGen
- You have Gmail MCP access enabled

### "No topic provided"

The payload must include a `topic` field:
```json
{
  "payload": {
    "topic": "your topic"
  }
}
```

### Agent doesn't create drafts

Check the logs:
```bash
# Local
# Check terminal output

# Railway
railway logs --follow
```

Look for Gmail tool execution logs.

## Customization

### Change Email Format

Edit `.claude/agents/poem-email-drafter.md`:
- Adjust poem length (change "8-16 lines")
- Modify poem style instructions
- Add email signature
- Include custom formatting

### Add Default Recipient

Modify the agent to use a specific email:
```markdown
- `to`: Recipient email address (default: "your-email@example.com")
```

### Use Different Subject Lines

Update the subject line pattern in the agent instructions.

## Tips

1. **Be specific with topics**: "autumn leaves falling" works better than just "autumn"
2. **Check drafts regularly**: Drafts pile up, remember to send or delete them
3. **Test with various topics**: The agent adapts its style to different themes
4. **Monitor logs**: Watch for successful draft creation confirmations

## Integration Ideas

### Webhook from Other Apps

Connect to:
- Slack: `/poem [topic]` command
- Discord: Bot command
- Zapier: Trigger on calendar events
- GitHub: Comment on issues with poems
- IFTTT: Daily poem about the weather

### Batch Processing

Send multiple topics:
```bash
for topic in "morning coffee" "evening sunset" "midnight rain"; do
  curl -X POST $URL/run \
    -H "Content-Type: application/json" \
    -d "{\"payload\": {\"topic\": \"$topic\"}}"
  sleep 2
done
```

## Related Examples

- **email-drafter**: Personalized re-engagement emails
- **enrichment**: LinkedIn profile enrichment

## Support

- Main documentation: [README.md](../../README.md)
- Railway deployment: [RAILWAY_DEPLOY.md](../../RAILWAY_DEPLOY.md)
- Agent writing guide: [.claude/agents/README.md](../../.claude/agents/README.md)
