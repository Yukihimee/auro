from typing import Any

from app.tools.mcp.base import MCPTool


class CalendarTool(MCPTool):
    name = "calendar_tool"

    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"tool": self.name, "action": action, "payload": payload, "status": "ok"}
