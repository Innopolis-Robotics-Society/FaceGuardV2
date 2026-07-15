"""Auth routes: login, logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import end_session, login, start_session
from ..database import FaceDatabase
from ..jinja import templates

router = APIRouter()


@router.get("/login")
async def login_page(request: Request):
    if request.session.get("admin_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": None},
    )


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: FaceDatabase = Depends(),
):
    try:
        admin = login(db, username, password)
    except Exception:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"},
            status_code=401,
        )
    start_session(request, admin)
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    end_session(request)
    return RedirectResponse("/login", status_code=303)
