from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Event
from app.schemas.event import EventCreate, EventRead

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("/events", response_model=EventRead)
def create_event(payload: EventCreate, db: Session = Depends(get_db_session)) -> Event:
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/events", response_model=list[EventRead])
def list_events(user_id: int, db: Session = Depends(get_db_session)) -> list[Event]:
    return list(db.scalars(select(Event).where(Event.user_id == user_id)).all())
