from fastapi import APIRouter

from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.notes import router as notes_router
from app.api.v1.endpoints.schedules import router as schedules_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.web_builder import router as web_builder_router
from app.api.v1.endpoints.workflows import router as workflows_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(dashboard_router)
api_router.include_router(tasks_router)
api_router.include_router(schedules_router)
api_router.include_router(notes_router)
api_router.include_router(workflows_router)
api_router.include_router(web_builder_router)
