from typing import Any

from app.agents.backend_agent import BackendAgent
from app.agents.design_agent import DesignAgent
from app.agents.frontend_agent import FrontendAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.quality_agent import QualityAgent
from app.agents.schedule_agent import ScheduleAgent
from app.agents.task_agent import TaskAgent
from app.services.llm import LLMClient
from app.tools.mcp.deploy_tool import DeployTool


class OrchestratorAgent:
    def __init__(self) -> None:
        self.task_agent = TaskAgent()
        self.schedule_agent = ScheduleAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.design_agent = DesignAgent()
        self.frontend_agent = FrontendAgent()
        self.backend_agent = BackendAgent()
        self.quality_agent = QualityAgent()
        self.deploy_tool = DeployTool()
        self.llm = LLMClient()

    async def route(self, request_text: str, payload: dict[str, Any]) -> dict[str, Any]:
        lowered = request_text.lower()
        if "task" in lowered or "todo" in lowered:
            return {"selected_agent": self.task_agent.name, "result": await self.task_agent.handle(payload)}
        if "calendar" in lowered or "schedule" in lowered or "meeting" in lowered:
            return {
                "selected_agent": self.schedule_agent.name,
                "result": await self.schedule_agent.handle(payload),
            }
        if "note" in lowered or "summary" in lowered:
            return {
                "selected_agent": self.knowledge_agent.name,
                "result": await self.knowledge_agent.handle(payload),
            }

        llm_result = await self.llm.chat(
            "Classify this request into one of [task_agent, schedule_agent, knowledge_agent]: "
            f"{request_text}"
        )
        return {
            "selected_agent": "llm_router",
            "result": llm_result,
        }

    async def route_web_builder(self, request_text: str, payload: dict[str, Any]) -> dict[str, Any]:
        design_result = await self.design_agent.handle(payload)
        frontend_result = await self.frontend_agent.handle(payload | {"design": design_result})
        backend_result = await self.backend_agent.handle(payload | {"design": design_result})
        quality_result = await self.quality_agent.handle(
            {
                "request_text": request_text,
                "design": design_result,
                "frontend": frontend_result,
                "backend": backend_result,
            }
        )
        deploy_result = await self.deploy_tool.execute(
            action="package_cloud_run",
            payload={"app_slug": payload.get("app_slug", "auro-generated-site")},
        )

        return {
            "selected_agent": "web_builder_orchestrator",
            "result": {
                "design": design_result,
                "frontend": frontend_result,
                "backend": backend_result,
                "quality": quality_result,
                "deploy": deploy_result,
            },
        }
