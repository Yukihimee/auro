from typing import Any

from app.agents.base import BaseAgent
from app.tools.mcp.task_tool import TaskTool


class TaskAgent(BaseAgent):
    name = "task_agent"

    def __init__(self) -> None:
        self.tool = TaskTool()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "list")
        return await self.tool.execute(action=action, payload=payload)
