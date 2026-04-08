from typing import Any

from app.agents.base import BaseAgent
from app.tools.mcp.notes_tool import NotesTool


class KnowledgeAgent(BaseAgent):
    name = "knowledge_agent"

    def __init__(self) -> None:
        self.tool = NotesTool()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "summarize")
        return await self.tool.execute(action=action, payload=payload)
