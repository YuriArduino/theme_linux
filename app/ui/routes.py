"""FastAPI routes for themectl local web app."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.theme_service import ThemeService

router = APIRouter()
templates = Jinja2Templates(directory="app/ui/templates")
service = ThemeService()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api/themes")
def themes(sort: str = Query(default="top", pattern="^(top|trending)$")):
    data = service.browse(sort)
    return [theme.__dict__ for theme in data]


@router.get("/api/themes/search")
def search(query: str = Query(min_length=2)):
    return [theme.__dict__ for theme in service.search(query)]


@router.get("/api/themes/{content_id}")
def details(content_id: str):
    theme = service.details(content_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme.__dict__


@router.get("/api/installed")
def installed():
    return service.installed()


@router.get("/api/updates")
def updates():
    return service.updates()


@router.post("/api/themes/{content_id}/install")
def install(content_id: str):
    try:
        return service.install(content_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/api/themes/{content_id}")
def remove(content_id: str):
    removed = service.remove(content_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Installed theme not found")
    return {"success": True, "id": content_id}
