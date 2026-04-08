# auro web-builder architecture (phase 1)

## Goal
Add a production-grade multi-agent web generation workflow that supports:
- prompt-only input
- prompt + references
- Figma link input
- Cloud Run deploy packaging output

## Pipeline
1. `POST /api/v1/web-builder/execute` accepts user request and input bundle.
2. `WorkflowEngine.execute_web_builder()` persists run metadata and delegates to orchestrator.
3. `OrchestratorAgent.route_web_builder()` executes:
   - `DesignAgent`
   - `FrontendAgent`
   - `BackendAgent`
   - `QualityAgent`
   - MCP deploy packaging via `DeployTool`
4. Results are persisted in `workflow_runs` and `tool_execution_logs`.
5. `GET /api/v1/web-builder/{workflow_id}` returns status/result.

## Model routing
- `ModelRouter` chooses provider by stage.
- Supported providers in phase 1:
  - `ollama` (local / default)
  - `cloud` (API-key based provider endpoint)
- Fallback behavior:
  - `WEB_BUILDER_PRIMARY_PROVIDER`
  - `WEB_BUILDER_FALLBACK_PROVIDER`
  - stage-level override via `WEB_BUILDER_FORCE_CLOUD_FOR_DESIGN`

## MCP tool contracts
Added MCP tools for web-builder flow:
- `design_tool.py` for design-spec extraction
- `component_tool.py` for component planning
- `deploy_tool.py` for Cloud Run packaging metadata

All tools follow the existing `MCPTool` contract in `app/tools/mcp/base.py`.

## Environment keys
Non-secret:
- `WEB_BUILDER_PRIMARY_PROVIDER`
- `WEB_BUILDER_FALLBACK_PROVIDER`
- `WEB_BUILDER_FORCE_CLOUD_FOR_DESIGN`
- `CLOUD_LLM_BASE_URL`
- `OLLAMA_BASE_URL`, `OLLAMA_MODEL`

Secrets (recommended):
- `CLOUD_LLM_API_KEY`
- `CLOUD_LLM_MODEL` (optional, if managed as secret)
- DB credentials or `DATABASE_URL`
