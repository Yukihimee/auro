from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema, PrioritySchema, TaskStatusSchema, TimestampedSchema


class TaskCreate(BaseSchema):
    user_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: PrioritySchema = PrioritySchema.medium
    due_at: datetime | None = None


class TaskUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatusSchema | None = None
    priority: PrioritySchema | None = None
    due_at: datetime | None = None


class TaskRead(TimestampedSchema):
    id: int
    user_id: int
    title: str
    description: str | None
    status: TaskStatusSchema
    priority: PrioritySchema
    due_at: datetime | None
