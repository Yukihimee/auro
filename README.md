# auro

Production-grade backend scaffold for a multi-agent AI system that coordinates tasks, schedules, and knowledge workflows.

## High-Level Architecture

- **API Layer** (`FastAPI`): REST endpoints for tasks, notes, schedules, workflow execution.
- **Workflow Engine**: Executes multi-step requests and persists orchestration history.
- **Primary Orchestrator Agent**: Routes user intent to specialized sub-agents.
- **Sub-Agents**:
  - `TaskAgent` for task operations
  - `ScheduleAgent` for calendar operations
  - `KnowledgeAgent` for notes and summarization
- **Tool Layer (MCP-style)**: Modular tool interfaces and adapters (`task`, `calendar`, `notes`, `reminder`).
- **Database Layer** (`PostgreSQL + SQLAlchemy`): Stores users, tasks, notes, events, workflow runs, decision logs, tool executions.
- **LLM Provider Layer** (`Ollama` abstraction): Swappable model client with retries.

## Stack Confirmation

- Backend: `FastAPI`
- LLM abstraction: `Ollama` (Qwen default model)
- Database: `PostgreSQL`
- ORM: `SQLAlchemy`
- API style: `REST`
- Deployment-ready direction: `Cloud Run`, `Secret Manager`, `Cloud SQL`, OAuth-ready architecture

## Project Structure

```text
app/
  agents/       # orchestrator + domain sub-agents
  api/v1/       # versioned REST endpoints
  core/         # config + logging
  db/           # engine/session + base
  models/       # SQLAlchemy entities
  schemas/      # Pydantic request/response contracts
  services/     # external provider clients (LLM)
  tools/mcp/    # MCP-style tool abstractions/adapters
  workflows/    # workflow execution engine
docs/skill.md   # mandatory project engineering standard
```

## Phase Plan

### Phase 1 (implemented)
- Scaffold production backend modules with clean boundaries
- Add core entities and request/response schemas
- Add orchestrator, sub-agents, and MCP-style tool contracts
- Add workflow execution + persistence of decisions/tool logs
- Expose initial REST endpoints

### Phase 2 (next)
- Real MCP integrations (Google Calendar, task provider, notes provider)
- Stronger intent planner + tool/action policies
- Alembic migrations and seed scripts
- Auth foundation and tenant-safe access patterns

### Phase 3
- Async job execution for long workflows
- Monitoring, traces, metrics, structured audit logs
- Cloud Run deployment assets + GCP service wiring

## Run Locally

1. Create environment and install dependencies:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Configure environment:
   - `cp .env.example .env`
   - Either set `DATABASE_URL`, or set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - For your AlloyDB setup:
     - `DB_HOST=10.30.0.5`
     - `DB_PORT=5432`
     - `DB_NAME=postgres`
     - `DB_USER=postgres`
     - `DB_PASSWORD=<your password>`
3. Ensure network reachability:
   - AlloyDB private IP requires running this API inside the same VPC (or via secure tunnel/proxy).
4. Run migrations:
   - `alembic upgrade head`
5. Start the API:
   - `uvicorn app.main:app --reload`
6. Open docs:
   - `http://127.0.0.1:8000/docs`

## Initial API Surface

- `GET /api/v1/health`
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `POST /api/v1/tasks`
- `GET /api/v1/tasks?user_id=<id>`
- `PATCH /api/v1/tasks/{task_id}`
- `POST /api/v1/schedules/events`
- `GET /api/v1/schedules/events?user_id=<id>`
- `POST /api/v1/notes`
- `GET /api/v1/notes?user_id=<id>`
- `POST /api/v1/workflows/execute`
- `POST /api/v1/web-builder/execute`
- `GET /api/v1/web-builder/{workflow_id}`

## GCP Deployment

- Use `scripts/deploy_cloud_run.sh` for container build + Cloud Run deployment.
- Full instructions: `docs/gcp-deploy.md`.
