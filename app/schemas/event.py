from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema, TimestampedSchema


class EventCreate(BaseSchema):
    user_id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    location: str | None = None
    event_metadata: dict | None = Field(default=None, validation_alias="metadata", serialization_alias="metadata")


class EventRead(TimestampedSchema):
    id: int
    user_id: int
    title: str
    starts_at: datetime
    ends_at: datetime
    location: str | None
    event_metadata: dict | None = Field(
        default=None, validation_alias="metadata", serialization_alias="metadata"
    )
