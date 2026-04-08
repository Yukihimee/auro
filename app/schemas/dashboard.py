from app.schemas.common import BaseSchema


class DashboardTaskItem(BaseSchema):
    title: str
    agent: str
    status: str


class DashboardLogItem(BaseSchema):
    time: str
    agent: str
    message: str


class DashboardMemoryItem(BaseSchema):
    label: str
    percent: int
    color: str


class DashboardOverviewResponse(BaseSchema):
    tasks_dispatched: int
    workflows_complete: int
    tool_calls_per_min: int
    running_count: int
    queued_count: int
    tasks: list[DashboardTaskItem]
    logs: list[DashboardLogItem]
    tools: list[str]
    memory: list[DashboardMemoryItem]
    degraded: bool = False
