from typing import Any

from app.tools.mcp.base import MCPTool


class DesignTool(MCPTool):
    name = "design_tool"

    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action == "extract_design_spec":
            return {
                "tool": self.name,
                "action": action,
                "status": "ok",
                "design_spec": {
                    "style_hint": payload.get("style_hint") or "modern clean",
                    "figma_url": payload.get("figma_url"),
                    "reference_urls": payload.get("reference_urls", []),
                    "reference_images": payload.get("reference_images", []),
                    "layout_principles": ["clear hierarchy", "8px spacing scale", "responsive sections"],
                },
            }
        return {"tool": self.name, "action": action, "payload": payload, "status": "ok"}
