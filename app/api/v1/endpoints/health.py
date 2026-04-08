from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/live")
def liveness_check() -> dict[str, str]:
    # Liveness should not depend on downstream systems.
    return {"status": "ok"}


@router.get("/ready", response_model=None)
def readiness_check() -> JSONResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unreachable"},
        )

    return JSONResponse(
        status_code=200,
        content={"status": "ready", "database": "ok"},
    )
