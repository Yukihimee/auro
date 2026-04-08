from typing import Any

from app.agents.base import BaseAgent
from app.services.model_router import ModelRouter


class BackendAgent(BaseAgent):
    name = "backend_agent"

    def __init__(self) -> None:
        self.model_router = ModelRouter()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_result = await self.model_router.generate(
            stage="backend",
            prompt=(
                "Propose backend API and data contracts for this website generation request: "
                f"{payload}"
            ),
        )
        return {
            "agent": self.name,
            "backend_outline": {
                "api_style": "REST",
                "auth": "token-ready",
                "data_storage": "postgresql",
            },
            "model_result": model_result,
        }
