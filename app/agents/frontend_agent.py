from typing import Any

from app.agents.base import BaseAgent
from app.services.model_router import ModelRouter
from app.tools.mcp.component_tool import ComponentTool


class FrontendAgent(BaseAgent):
    name = "frontend_agent"

    def __init__(self) -> None:
        self.tool = ComponentTool()
        self.model_router = ModelRouter()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        component_plan = await self.tool.execute(action="generate_component_plan", payload=payload)
        model_result = await self.model_router.generate(
            stage="frontend",
            prompt=(
                "Generate a frontend implementation outline with pages and components. "
                f"Component plan: {component_plan}"
            ),
        )
        return {
            "agent": self.name,
            "component_plan": component_plan,
            "model_result": model_result,
        }
