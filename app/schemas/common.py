from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class TaskStatusSchema(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class PrioritySchema(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    message: str


class TimestampedSchema(BaseSchema):
    created_at: datetime
