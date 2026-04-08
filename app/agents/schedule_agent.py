from typing import Any

from app.agents.base import BaseAgent
from app.tools.mcp.calendar_tool import CalendarTool


class ScheduleAgent(BaseAgent):
    name = "schedule_agent"

    def __init__(self) -> None:
        self.tool = CalendarTool()

    async def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action", "list")
        return await self.tool.execute(action=action, payload=payload)
