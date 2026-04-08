from typing import Any

from app.agents.base import BaseAgent
from app.services.model_router import ModelRouter
from app.tools.mcp.design_tool import DesignTool
from app.tools.mcp.stitch_tool import StitchTool


class DesignAgent(BaseAgent):
    name = "design_agent"

    def __init__(self) -> None:
        self.tool = DesignTool()
        self.stitch_tool = StitchTool()
        self.model_router = ModelRouter()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        spec_result = await self.tool.execute(action="extract_design_spec", payload=payload)
        stitch_result = await self.stitch_tool.execute(action="generate_design_context", payload=payload)
        stitch_context = stitch_result.get("result") if stitch_result.get("status") == "ok" else None
        model_result = await self.model_router.generate(
            stage="design",
            prompt=(
                "Create a concise UI design system spec for a web app from this input: "
                f"{spec_result['design_spec']}. Stitch context: {stitch_context}"
            ),
        )
        return {
            "agent": self.name,
            "design_spec": spec_result["design_spec"],
            "stitch_result": stitch_result,
            "model_result": model_result,
        }
