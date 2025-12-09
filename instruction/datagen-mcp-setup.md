# DataGen MCP Setup for Claude Code

Use these steps before running the **email-drafter** agent so it can call DataGen tools.

1. Install the DataGen MCP server (Claude Code supports MCP servers):
   - Follow the quickstart at https://github.com/datagendev/datagen-python-sdk (look for the MCP section).
2. In Claude desktop, open **Settings → Developer → MCP Servers** and add a new server:
   - **Command**: `datagen-mcp` (or the path from the quickstart)
   - **Working directory**: your project root
   - Ensure the server starts without errors.
3. Set the required environment variable so the server can authenticate:
   - `DATAGEN_API_KEY=<your key>`
4. Restart Claude Code (or reload MCP servers) and confirm DataGen tools appear, e.g. `mcp_Neon_run_sql`.
5. Run the **email-drafter** agent; it will now be able to call DataGen tools via MCP.

Notes:
- Keep `permission_mode=bypassPermissions` in this repo’s settings when running inside the Docker/non-root setup.
- If tools aren’t visible, re-check the MCP server logs in Claude Code and that the API key is present.
