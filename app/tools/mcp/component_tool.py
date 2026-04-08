from typing import Any

from app.tools.mcp.base import MCPTool


class ComponentTool(MCPTool):
    name = "component_tool"

    async def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action == "generate_component_plan":
            return {
                "tool": self.name,
                "action": action,
                "status": "ok",
                "components": [
                    "Navbar",
                    "Hero",
                    "FeatureGrid",
                    "Testimonials",
                    "Pricing",
                    "Footer",
                ],
                "target_framework": payload.get("target_framework", "nextjs"),
                "style_system": payload.get("target_style_system", "tailwind"),
            }
        return {"tool": self.name, "action": action, "payload": payload, "status": "ok"}
