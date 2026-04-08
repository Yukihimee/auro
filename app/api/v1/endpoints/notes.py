from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.entities import Note
from app.schemas.note import NoteCreate, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteRead)
def create_note(payload: NoteCreate, db: Session = Depends(get_db_session)) -> Note:
    note = Note(**payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[NoteRead])
def list_notes(user_id: int, db: Session = Depends(get_db_session)) -> list[Note]:
    return list(db.scalars(select(Note).where(Note.user_id == user_id)).all())
