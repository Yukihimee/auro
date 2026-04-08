from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.web_builder import (
    WebBuilderRequest,
    WebBuilderResponse,
    WebBuilderStatusResponse,
)
from app.workflows.engine import WorkflowEngine

router = APIRouter(prefix="/web-builder", tags=["web-builder"])
workflow_engine = WorkflowEngine()


@router.post("/execute", response_model=WebBuilderResponse)
async def execute_web_builder(
    payload: WebBuilderRequest, db: Session = Depends(get_db_session)
) -> WebBuilderResponse:
    run = await workflow_engine.execute_web_builder(
        db=db,
        user_id=payload.user_id,
        request_text=payload.request_text,
        builder_input=payload.input.model_dump(),
    )
    return WebBuilderResponse(
        workflow_id=run.id,
        status=run.status,
        result=run.result,
        created_at=run.created_at,
    )


@router.get("/{workflow_id}", response_model=WebBuilderStatusResponse)
def get_web_builder_status(workflow_id: int, db: Session = Depends(get_db_session)) -> WebBuilderStatusResponse:
    run = workflow_engine.get_workflow_run(db=db, workflow_id=workflow_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return WebBuilderStatusResponse(
        workflow_id=run.id,
        status=run.status,
        result=run.result,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )
