from datetime import datetime

from app.schemas.common import BaseSchema


class WorkflowRequest(BaseSchema):
    user_id: int
    request_text: str


class WorkflowResponse(BaseSchema):
    workflow_id: int
    status: str
    result: dict | None
    created_at: datetime
