"""Admin console FastAPI sub-application."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
try:
    _templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
except AssertionError:  # pragma: no cover - fallback for minimal test envs
    _templates = None

app = FastAPI(title="Whalez-AI Admin Console")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    if _templates is None:
        return HTMLResponse("<h1>Whalez-AI Console</h1>")
    return _templates.TemplateResponse("index.html", {"request": request})
