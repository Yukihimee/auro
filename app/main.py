from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
ui_dir = Path(__file__).resolve().parent / "ui"

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount("/ui", StaticFiles(directory=ui_dir), name="ui")


@app.get("/", response_class=FileResponse)
def web_builder_ui() -> FileResponse:
    return FileResponse(ui_dir / "index.html")
