from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Event, Note, Task, ToolExecutionLog, WorkflowRun
from app.schemas.dashboard import (
    DashboardLogItem,
    DashboardMemoryItem,
    DashboardOverviewResponse,
    DashboardTaskItem,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _default_response() -> DashboardOverviewResponse:
    return DashboardOverviewResponse(
        tasks_dispatched=0,
        workflows_complete=0,
        tool_calls_per_min=0,
        running_count=0,
        queued_count=0,
        tasks=[],
        logs=[],
        tools=[],
        memory=[
            DashboardMemoryItem(label="tasks", percent=0, color="#6366f1"),
            DashboardMemoryItem(label="notes", percent=0, color="#10b981"),
            DashboardMemoryItem(label="events", percent=0, color="#f59e0b"),
            DashboardMemoryItem(label="logs", percent=0, color="#e24b4a"),
        ],
        degraded=True,
    )


@router.get("/overview", response_model=DashboardOverviewResponse)
def dashboard_overview(user_id: int, db: Session = Depends(get_db_session)) -> DashboardOverviewResponse:
    try:
        task_count = int(db.scalar(select(func.count()).select_from(Task).where(Task.user_id == user_id)) or 0)
        workflow_complete = int(
            db.scalar(
                select(func.count())
                .select_from(WorkflowRun)
                .where(WorkflowRun.user_id == user_id, WorkflowRun.status == "completed")
            )
            or 0
        )

        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        tool_calls_per_min = int(
            db.scalar(
                select(func.count())
                .select_from(ToolExecutionLog)
                .where(ToolExecutionLog.executed_at >= one_minute_ago)
            )
            or 0
        )

        running_count = int(
            db.scalar(
                select(func.count()).select_from(Task).where(
                    Task.user_id == user_id,
                    Task.status == "in_progress",
                )
            )
            or 0
        )
        queued_count = int(
            db.scalar(
                select(func.count()).select_from(Task).where(
                    Task.user_id == user_id,
                    Task.status == "pending",
                )
            )
            or 0
        )

        task_rows = list(
            db.scalars(
                select(Task)
                .where(Task.user_id == user_id)
                .order_by(Task.updated_at.desc())
                .limit(4)
            )
        )
        tasks = [
            DashboardTaskItem(
                title=t.title,
                agent="orion",
                status=t.status.value if hasattr(t.status, "value") else str(t.status),
            )
            for t in task_rows
        ]

        log_rows = list(
            db.scalars(
                select(ToolExecutionLog)
                .order_by(ToolExecutionLog.executed_at.desc())
                .limit(10)
            )
        )
        logs = [
            DashboardLogItem(
                time=row.executed_at.strftime("%H:%M:%S"),
                agent=row.tool_name,
                message=f"status={row.status}",
            )
            for row in log_rows
        ]

        tool_rows = list(
            db.scalars(
                select(ToolExecutionLog.tool_name)
                .distinct()
                .order_by(ToolExecutionLog.tool_name.asc())
                .limit(8)
            )
        )
        tools = [t for t in tool_rows if t]

        notes_count = int(db.scalar(select(func.count()).select_from(Note).where(Note.user_id == user_id)) or 0)
        events_count = int(db.scalar(select(func.count()).select_from(Event).where(Event.user_id == user_id)) or 0)
        logs_count = int(db.scalar(select(func.count()).select_from(ToolExecutionLog)) or 0)

        memory = [
            DashboardMemoryItem(label="tasks", percent=min(100, task_count), color="#6366f1"),
            DashboardMemoryItem(label="notes", percent=min(100, notes_count), color="#10b981"),
            DashboardMemoryItem(label="events", percent=min(100, events_count), color="#f59e0b"),
            DashboardMemoryItem(label="logs", percent=min(100, logs_count), color="#e24b4a"),
        ]

        return DashboardOverviewResponse(
            tasks_dispatched=task_count,
            workflows_complete=workflow_complete,
            tool_calls_per_min=tool_calls_per_min,
            running_count=running_count,
            queued_count=queued_count,
            tasks=tasks,
            logs=logs,
            tools=tools,
            memory=memory,
            degraded=False,
        )
    except SQLAlchemyError:
        return _default_response()
