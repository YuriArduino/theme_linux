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
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.get("/api/themes")
def themes(
    sort: str = Query(default="top", pattern="^(top|trending)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=60),
    category: str | None = Query(default=None),
):
    data = service.browse(sort, page=page, page_size=page_size, category=category)
    items = [theme.to_dict() for theme in data["items"]]
    print(
        f"[themectl][routes:/api/themes] sort={sort} page={page} page_size={page_size} category={category!r} items={len(items)}"
    )
    return {**data["pagination"], "items": items}


@router.get("/api/themes/search")
def search(
    query: str = Query(min_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=60),
    category: str | None = Query(default=None),
):
    data = service.search(query, page=page, page_size=page_size, category=category)
    items = [theme.to_dict() for theme in data["items"]]
    print(
        f"[themectl][routes:/api/themes/search] query={query!r} page={page} page_size={page_size} category={category!r} items={len(items)}"
    )
    return {**data["pagination"], "items": items}


@router.get("/api/categories")
def categories():
    items = service.categories()
    print(f"[themectl][routes:/api/categories] items={len(items)}")
    return items


@router.get("/api/themes/{content_id}")
def details(content_id: str):
    theme = service.details(content_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    print(f"[themectl][routes:/api/themes/{{content_id}}] id={content_id} found=True")
    return theme.to_dict()


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
