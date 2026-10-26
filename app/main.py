import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from atelier.exports import markdown_export
from atelier.schemas import Dimension, Studio
from atelier.scoring import rank_use_cases
from atelier.settings import Settings
from atelier.store import PERSONAS, SessionStore, load_fixture

ROOT = Path(__file__).resolve().parent
settings = Settings()
store = SessionStore()
COOKIE = "studio_session"
MAX_IMPORT_BYTES = 512_000


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    async def cleanup() -> None:
        while True:
            await asyncio.sleep(30)
            store.purge()

    task = asyncio.create_task(cleanup())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        store.clear()


app = FastAPI(
    title="PartnershipsStudio", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")


def safe_url(value: str) -> str | None:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if any(ord(char) < 32 for char in value):
        return None
    return value if parsed.scheme in ("https", "http") and parsed.netloc else None


templates.env.filters["safe_url"] = safe_url


@app.middleware("http")
async def security_headers(request: Request, call_next: RequestResponseEndpoint) -> Response:
    if request.method in ("POST", "DELETE", "PUT", "PATCH"):
        if request.headers.get("origin") != str(request.base_url).rstrip("/"):
            return JSONResponse({"detail": "Open this action from the same app."}, status_code=403)
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    if request.url.path.startswith("/studio") or request.url.path == "/session/heartbeat":
        token = request.cookies.get(COOKIE)
        if token and store.get(token) is not None:
            set_session_cookie(response, token, request)
    return response


def set_session_cookie(response: Response, token: str, request: Request) -> None:
    response.set_cookie(
        COOKIE,
        token,
        max_age=1800,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
    )


def page(request: Request, name: str, **context: Any) -> Response:
    return templates.TemplateResponse(
        request=request, name=name, context={"mode": "demo", **context}
    )


def current(request: Request) -> Studio:
    studio = store.get(request.cookies.get(COOKIE))
    if studio is None:
        raise HTTPException(410, "Session expired. Reopen an example or import your saved JSON.")
    return studio


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return page(request, "home.html", examples=[load_fixture(p) for p in PERSONAS])


@app.get("/examples/{persona}/{variant}")
async def open_example(request: Request, persona: str, variant: str) -> Response:
    try:
        studio = load_fixture(persona, variant)
    except ValueError as error:
        raise HTTPException(404, "Example not found") from error
    store.delete(request.cookies.get(COOKIE))
    response = RedirectResponse("/studio", status_code=303)
    set_session_cookie(response, store.create(studio), request)
    return response


@app.get("/studio", response_class=HTMLResponse)
async def studio_page(request: Request) -> Response:
    try:
        studio = current(request)
    except HTTPException:
        return page(request, "expired.html")
    return page(
        request,
        "studio.html",
        studio=studio,
        ranked=rank_use_cases(studio.use_cases, studio.scoring_weights),
        weights=studio.scoring_weights,
        dimensions=list(Dimension),
        sample_available=studio.id in PERSONAS and studio.fictional,
    )


@app.get("/studio/data")
async def studio_data(request: Request) -> Response:
    return JSONResponse(current(request).model_dump(mode="json"))


@app.get("/studio/export/{format_name}")
async def export(request: Request, format_name: str, weights: str | None = None) -> Response:
    studio = current(request)
    if weights is not None:
        if len(weights) > 1000:
            raise HTTPException(400, "Invalid scoring weights")
        try:
            studio = Studio.model_validate(
                {**studio.model_dump(), "scoring_weights": json.loads(weights)}
            )
        except (ValueError, ValidationError) as error:
            raise HTTPException(400, "Invalid scoring weights") from error
    if format_name == "json":
        content = studio.model_dump_json(indent=2)
        media = "application/json"
    elif format_name == "md":
        content = markdown_export(studio)
        media = "text/markdown"
    else:
        raise HTTPException(404, "Export format not supported")
    return Response(
        content,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{studio.id}.{format_name}"'},
    )


@app.post("/studio/import")
async def import_studio(request: Request) -> Response:
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_IMPORT_BYTES:
            raise HTTPException(413, "JSON must be smaller than 500 KB")
    try:
        studio = Studio.model_validate_json(bytes(body))
    except ValidationError as error:
        raise HTTPException(
            422, "This file does not match the studio schema. Nothing was imported."
        ) from error
    store.delete(request.cookies.get(COOKIE))
    response = JSONResponse({"url": "/studio"})
    set_session_cookie(response, store.create(studio), request)
    return response


@app.post("/session/heartbeat")
async def heartbeat(request: Request) -> Response:
    current(request)
    return Response(status_code=204)


@app.post("/session/clear")
async def clear_session(request: Request) -> Response:
    store.delete(request.cookies.get(COOKIE))
    response = JSONResponse({"url": "/"})
    response.delete_cookie(COOKIE)
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "milestone": "M1"}


@app.get("/status", response_class=HTMLResponse)
async def status(request: Request) -> Response:
    return page(request, "status.html", requested_mode=settings.app_mode)


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> Response:
    return page(request, "privacy.html")


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request) -> Response:
    return page(request, "report.html")
