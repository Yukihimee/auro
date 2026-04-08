import asyncio

from app.agents.orchestrator import OrchestratorAgent


def test_web_builder_route_returns_all_sections() -> None:
    orchestrator = OrchestratorAgent()

    async def fake_design(payload: dict) -> dict:
        return {"agent": "design_agent", "design_spec": {"style": "modern"}}

    async def fake_frontend(payload: dict) -> dict:
        return {"agent": "frontend_agent", "pages": ["home"]}

    async def fake_backend(payload: dict) -> dict:
        return {"agent": "backend_agent", "api": ["/api/v1"]}

    async def fake_quality(payload: dict) -> dict:
        return {"agent": "quality_agent", "checks": ["ok"]}

    async def fake_deploy(action: str, payload: dict) -> dict:
        return {"tool": "deploy_tool", "action": action, "status": "ok"}

    orchestrator.design_agent.handle = fake_design  # type: ignore[method-assign]
    orchestrator.frontend_agent.handle = fake_frontend  # type: ignore[method-assign]
    orchestrator.backend_agent.handle = fake_backend  # type: ignore[method-assign]
    orchestrator.quality_agent.handle = fake_quality  # type: ignore[method-assign]
    orchestrator.deploy_tool.execute = fake_deploy  # type: ignore[method-assign]

    result = asyncio.run(
        orchestrator.route_web_builder(
            request_text="build me a marketing site",
            payload={"user_id": 1, "prompt": "landing page"},
        )
    )
    assert result["selected_agent"] == "web_builder_orchestrator"
    assert "design" in result["result"]
    assert "frontend" in result["result"]
    assert "backend" in result["result"]
    assert "quality" in result["result"]
    assert "deploy" in result["result"]
