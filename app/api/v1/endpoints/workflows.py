from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.workflow import WorkflowRequest, WorkflowResponse
from app.workflows.engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["workflows"])
workflow_engine = WorkflowEngine()


@router.post("/execute", response_model=WorkflowResponse)
async def execute_workflow(
    payload: WorkflowRequest, db: Session = Depends(get_db_session)
) -> WorkflowResponse:
    run = await workflow_engine.execute(db=db, user_id=payload.user_id, request_text=payload.request_text)
    return WorkflowResponse(
        workflow_id=run.id,
        status=run.status,
        result=run.result,
        created_at=run.created_at,
    )
