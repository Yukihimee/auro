from typing import Any

from app.agents.base import BaseAgent
from app.services.model_router import ModelRouter
from app.tools.mcp.design_tool import DesignTool


class DesignAgent(BaseAgent):
    name = "design_agent"

    def __init__(self) -> None:
        self.tool = DesignTool()
        self.model_router = ModelRouter()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        spec_result = await self.tool.execute(action="extract_design_spec", payload=payload)
        model_result = await self.model_router.generate(
            stage="design",
            prompt=(
                "Create a concise UI design system spec for a web app from this input: "
                f"{spec_result['design_spec']}"
            ),
        )
        return {
            "agent": self.name,
            "design_spec": spec_result["design_spec"],
            "model_result": model_result,
        }
