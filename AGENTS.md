# Repository Guidelines

## Project Structure & Module Organization
- `app/main.py`: FastAPI entrypoint and HTTP middleware; background tasks live here.
- `app/agent.py`: Agent discovery, MCP config, and execution pipeline.
- `app/config.py` & `app/models.py`: Pydantic settings and response/request schemas.
- `.claude/agents/`: Source of agent prompts (`default.md`, examples, README for format); discovery follows `AGENT_FILE_PATH` → `AGENT_NAME` → auto-detect → `default.md`.
- `scripts/`: Helper workflows (`init-agent.sh`, `test-local.sh`, `deploy.sh`).
- `examples/`: Ready-to-copy agent templates (email drafter, poem).
- Supporting files: `Dockerfile`, `Procfile`, `requirements.txt`, `railway.json`, `runtime.txt`.

## Build, Test, and Development Commands
- Install deps: `pip install -r requirements.txt` (Python 3.13 recommended).
- Run dev server: `uvicorn app.main:app --reload` (defaults to port `8000`; override with `PORT`).
- Quick local smoke test (health, agent metadata, run flow): `./scripts/test-local.sh` (spawns server on `8001`).
- Create a new agent file with boilerplate frontmatter: `./scripts/init-agent.sh <agent-name>`.
- Deploy to Railway (non-blocking): `./scripts/deploy.sh` after `.env` is configured.

## API Modes
- `POST /run`: Queues execution in background; returns request_id immediately.
- `POST /run/sync`: Waits for completion and returns the full agent output in `result`.
- `POST /run/stream`: Streams text chunks via SSE (`text/event-stream`) and sets `X-Request-ID` header.

## Coding Style & Naming Conventions
- Follow PEP8 with 4-space indentation and type hints; keep functions small and documented with triple-quoted docstrings.
- Use snake_case for functions/vars, PascalCase for classes, SCREAMING_SNAKE_CASE for env-driven constants.
- Prefer structured JSON logging via `log_event` (see `app/agent.py`); avoid ad-hoc prints.
- Keep API models in `app/models.py`; add settings to `app/config.py` using `pydantic_settings.BaseSettings`.

## Testing Guidelines
- Primary check: `./scripts/test-local.sh` (expects `.env` with `ANTHROPIC_API_KEY`; optional `WEBHOOK_SECRET`).
- Add Python tests under `tests/` (pytest recommended) named `test_<module>.py`; include sample payloads for `/run` and schema validation.
- When adding features, provide at least one integration-style call using FastAPI TestClient and assert structured logs when feasible.

## Commit & Pull Request Guidelines
- Commit messages: short imperative summaries (e.g., `add agent auto-discovery guard`). History is minimal; Conventional Commits (`feat:`, `fix:`) are welcome but not required—choose consistency within the PR.
- PRs should include: concise description, linked issue/story, manual test notes (commands + outcomes), and screenshots or sample responses for API changes.
- Keep changes scoped; update docs (`README.md`, `.claude/agents/README.md`, or `AGENTS.md`) when user-facing behavior shifts.

## Security & Configuration Tips
- Never commit secrets; use `.env` locally and Railway variables in CI/CD. Required: `ANTHROPIC_API_KEY`; recommended for production: `WEBHOOK_SECRET` to enforce `X-API-Key` checks.
- Optional MCP access via `DATAGEN_API_KEY` enables the built-in DataGen server; remove unused credentials from `.env` before sharing.
- Validate agent selection with `AGENT_NAME` or `AGENT_FILE_PATH`; keep only one non-README `.md` in `.claude/agents` to avoid auto-detect ambiguity.
