from datetime import datetime
from typing import Any, Literal

from app.schemas.common import BaseSchema


class WebBuilderInput(BaseSchema):
    prompt: str
    reference_urls: list[str] = []
    reference_images: list[str] = []
    figma_url: str | None = None
    style_hint: str | None = None
    target_framework: str = "nextjs"
    target_style_system: str = "tailwind"


class WebBuilderRequest(BaseSchema):
    user_id: int
    request_text: str
    input: WebBuilderInput


class WebBuilderResponse(BaseSchema):
    workflow_id: int
    status: str
    result: dict[str, Any] | None
    created_at: datetime


class WebBuilderStatusResponse(BaseSchema):
    workflow_id: int
    status: Literal["running", "completed", "failed"]
    result: dict[str, Any] | None
    created_at: datetime
    completed_at: datetime | None
