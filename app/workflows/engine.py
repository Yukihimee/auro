from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import OrchestratorAgent
from app.models.entities import AgentDecisionLog, ToolExecutionLog, WorkflowRun


class WorkflowEngine:
    def __init__(self) -> None:
        self.orchestrator = OrchestratorAgent()

    async def execute(self, db: Session, user_id: int, request_text: str) -> WorkflowRun:
        workflow = WorkflowRun(user_id=user_id, request_text=request_text, status="running")
        db.add(workflow)
        db.flush()

        routed = await self.orchestrator.route(request_text=request_text, payload={"user_id": user_id})
        selected_agent = routed["selected_agent"]
        result: dict[str, Any] = routed["result"]

        db.add(
            AgentDecisionLog(
                workflow_run_id=workflow.id,
                agent_name="orchestrator_agent",
                decision={"selected_agent": selected_agent, "request_text": request_text},
            )
        )
        db.add(
            ToolExecutionLog(
                workflow_run_id=workflow.id,
                tool_name=selected_agent,
                input_payload={"user_id": user_id, "request_text": request_text},
                output_payload=result,
                status="success",
            )
        )

        workflow.status = "completed"
        workflow.result = {"selected_agent": selected_agent, "result": result}
        workflow.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(workflow)
        return workflow

    async def execute_web_builder(
        self, db: Session, user_id: int, request_text: str, builder_input: dict[str, Any]
    ) -> WorkflowRun:
        workflow = WorkflowRun(user_id=user_id, request_text=request_text, status="running")
        db.add(workflow)
        db.flush()

        routed = await self.orchestrator.route_web_builder(
            request_text=request_text,
            payload={"user_id": user_id, **builder_input},
        )
        selected_agent = routed["selected_agent"]
        result: dict[str, Any] = routed["result"]

        db.add(
            AgentDecisionLog(
                workflow_run_id=workflow.id,
                agent_name="web_builder_orchestrator",
                decision={
                    "selected_agent": selected_agent,
                    "request_text": request_text,
                    "input_type": "web_builder",
                },
            )
        )
        db.add(
            ToolExecutionLog(
                workflow_run_id=workflow.id,
                tool_name=selected_agent,
                input_payload={"user_id": user_id, "request_text": request_text, "builder_input": builder_input},
                output_payload=result,
                status="success",
            )
        )

        workflow.status = "completed"
        workflow.result = {"selected_agent": selected_agent, "result": result}
        workflow.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(workflow)
        return workflow

    def get_workflow_run(self, db: Session, workflow_id: int) -> WorkflowRun | None:
        return db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).one_or_none()
