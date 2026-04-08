from app.schemas.common import BaseSchema, TimestampedSchema


class NoteCreate(BaseSchema):
    user_id: int
    title: str
    body: str


class NoteRead(TimestampedSchema):
    id: int
    user_id: int
    title: str
    body: str
    summary: str | None
