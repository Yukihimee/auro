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
        schema = {
            "type": "object",
            "properties": {
                "selected_agent": {
                    "type": "string",
                    "enum": [
                        self.task_agent.name, 
                        self.schedule_agent.name, 
                        self.knowledge_agent.name, 
                        self.deploy_tool.name
                    ]
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation for why this agent was selected."
                }
            },
            "required": ["selected_agent", "reasoning"]
        }

        prompt = (
            f"You are a master orchestration agent. Route the following request to the correct sub-agent.\n"
            f"Request: {request_text}\n"
            f"Respond using the JSON schema provided."
        )

        try:
            import json
            llm_result = await self.llm.chat(
                prompt=prompt, 
                response_format=schema
            )
            # Ollama /api/generate returns the text in the "response" field
            response_json = json.loads(llm_result.get("response", "{}"))
            selected_agent_name = response_json.get("selected_agent")

            if selected_agent_name == self.task_agent.name:
                return {"selected_agent": selected_agent_name, "result": await self.task_agent.handle(payload)}
            elif selected_agent_name == self.schedule_agent.name:
                return {"selected_agent": selected_agent_name, "result": await self.schedule_agent.handle(payload)}
            elif selected_agent_name == self.knowledge_agent.name:
                return {"selected_agent": selected_agent_name, "result": await self.knowledge_agent.handle(payload)}
            else:
                return {"selected_agent": "unknown", "result": {"error": "Could not map to a standard agent."}}

        except Exception as e:
            # Fallback to basic if LLM fails
            return {
                "selected_agent": "error",
                "result": {"error": str(e)},
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
