from typing import Any

from app.agents.base import BaseAgent
from app.services.model_router import ModelRouter


class QualityAgent(BaseAgent):
    name = "quality_agent"

    def __init__(self) -> None:
        self.model_router = ModelRouter()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_result = await self.model_router.generate(
            stage="quality",
            prompt=(
                "Review this generated website plan for quality. "
                "Return accessibility, performance, and consistency checks: "
                f"{payload}"
            ),
        )
        return {
            "agent": self.name,
            "checks": ["accessibility", "performance", "consistency"],
            "model_result": model_result,
        }
