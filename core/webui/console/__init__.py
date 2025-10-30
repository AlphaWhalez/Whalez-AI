"""Admin console FastAPI sub-application."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
_templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Whalez-AI Admin Console")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return _templates.TemplateResponse("index.html", {"request": request})
