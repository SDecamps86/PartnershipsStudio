from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from atelier.settings import Settings

ROOT = Path(__file__).resolve().parent
settings = Settings()
app = FastAPI(title="PartnershipsStudio", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")


@app.middleware("http")
async def security_headers(request: Request, call_next: RequestResponseEndpoint) -> Response:
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response


def page(request: Request, name: str, **context: Any) -> Response:
    return templates.TemplateResponse(
        request=request, name=name, context={"mode": "demo", **context}
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return page(request, "home.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "milestone": "M0"}


@app.get("/status", response_class=HTMLResponse)
async def status(request: Request) -> Response:
    return page(request, "status.html", requested_mode=settings.app_mode)


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> Response:
    return page(request, "privacy.html")


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request) -> Response:
    return page(request, "report.html")
