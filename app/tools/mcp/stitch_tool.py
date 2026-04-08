from typing import Any

import httpx

from app.core.config import get_settings
from app.tools.mcp.base import MCPTool


class StitchTool(MCPTool):
    name = "stitch_tool"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action != "generate_design_context":
            return {"tool": self.name, "action": action, "payload": payload, "status": "ok"}

        if not self.settings.stitch_mcp_url:
            return {
                "tool": self.name,
                "action": action,
                "status": "skipped",
                "reason": "STITCH_MCP_URL not configured",
            }
        if not self.settings.stitch_mcp_api_key:
            return {
                "tool": self.name,
                "action": action,
                "status": "skipped",
                "reason": "STITCH_MCP_API_KEY not configured",
            }

        headers = {
            "Authorization": f"Bearer {self.settings.stitch_mcp_api_key}",
            "Content-Type": "application/json",
        }
        body = {"action": action, "payload": payload}
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(self.settings.stitch_mcp_url, json=body, headers=headers)
            response.raise_for_status()
            result = response.json()

        return {
            "tool": self.name,
            "action": action,
            "status": "ok",
            "result": result,
        }
