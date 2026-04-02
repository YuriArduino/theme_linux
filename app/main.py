"""Application entrypoint for themectl web UI."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.ui.routes import router
from app.utils.config import Settings


def create_app() -> FastAPI:
    Settings.ensure_directories()
    app = FastAPI(title="themectl", version=Settings.APP_VERSION)
    app.include_router(router)
    app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")
    return app


app = create_app()
