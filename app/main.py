import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from atelier.exports import markdown_export
from atelier.pipeline import dashboard
from atelier.schemas import Dimension, Studio, WeightUpdate
from atelier.scoring import rank_use_cases
from atelier.settings import Settings
from atelier.store import PERSONAS, SessionStore, load_fixture
from atelier.tracking import Stage, TaskUpdate, TrackingUpdate

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
app.mount(
    "/assets",
    StaticFiles(directory=ROOT.parent / "site/dist/assets", check_dir=False),
    name="demo-assets",
)
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
    if (
        request.url.path.startswith(("/studio", "/pipeline", "/partners"))
        or request.url.path == "/session/heartbeat"
    ):
        token = request.cookies.get(COOKIE)
        if token and store.exists(token):
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
    selected = store.get(request.cookies.get(COOKIE))
    return templates.TemplateResponse(
        request=request,
        name=name,
        context={"mode": "demo", "active_partner": selected, "active_tab": "", **context},
    )


def current(request: Request) -> Studio:
    studio = store.get(request.cookies.get(COOKIE))
    if studio is None:
        raise HTTPException(410, "Session expired. Reopen an example or import your saved JSON.")
    return studio


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    demo = ROOT.parent / "site/dist/index.html"
    if demo.exists():
        return FileResponse(demo)
    return page(
        request, "home.html", active_tab="prepare", examples=[load_fixture(p) for p in PERSONAS]
    )


def workspace_token(request: Request) -> tuple[str, bool]:
    token = request.cookies.get(COOKIE)
    if token and store.exists(token):
        return token, False
    return store.create(), True


@app.get("/pipeline", response_class=HTMLResponse)
async def pipeline_page(
    request: Request,
    q: str = "",
    stage: str = "",
    state: str = "",
    priority: str = "",
    audience: str = "",
    layout: str = "list",
) -> Response:
    if max(map(len, [q, stage, state, priority, audience])) > 200:
        raise HTTPException(400, "Filter text is too long")
    token, created = workspace_token(request)
    data = dashboard(
        store.list(token),
        datetime.now(ZoneInfo("America/Los_Angeles")).date(),
        q,
        stage,
        state,
        priority,
        audience,
    )
    response = page(
        request, "pipeline.html", active_tab="pipeline", board=layout == "board", **data
    )
    if created:
        set_session_cookie(response, token, request)
    return response


@app.get("/partners/{partner_id}")
async def select_partner(request: Request, partner_id: str, view: str = "overview") -> Response:
    token, _ = workspace_token(request)
    if not store.select(token, partner_id):
        raise HTTPException(404, "Partner not found in this workspace")
    response = RedirectResponse(
        f"/studio?view={view if view in VIEWS else 'overview'}", status_code=303
    )
    set_session_cookie(response, token, request)
    return response


@app.get("/examples/{persona}/{variant}")
async def open_example(request: Request, persona: str, variant: str) -> Response:
    try:
        studio = load_fixture(persona, variant)
    except ValueError as error:
        raise HTTPException(404, "Example not found") from error
    token, _ = workspace_token(request)
    existing = next((s for s in store.list(token) if s.id == persona), None)
    if existing and existing.variant == variant:
        store.select(token, persona)
    else:
        store.put(token, studio, preserve_tracking=True)
    response = RedirectResponse("/studio?view=overview", status_code=303)
    set_session_cookie(response, token, request)
    return response


VIEWS = {
    "overview": ("Overview", "overview"),
    "profile": ("Partner profile", "context"),
    "priorities": ("Priorities", "context"),
    "stakeholders": ("Stakeholders", "context"),
    "workflow": ("Workflow", "workflow"),
    "use-cases": ("Use cases", "use-cases"),
    "demo": ("Session plan", "session"),
    "experience": ("Experience design", "session"),
    "brief": ("Day brief", "session"),
    "journey": ("Journey", "plan"),
    "experiments": ("Experiments", "plan"),
    "cadence": ("90-day follow-up", "plan"),
    "feedback": ("Feedback & metrics", "plan"),
    "tasks": ("Preparation tasks", "plan"),
    "integrity": ("Sources & risks", "integrity"),
}


@app.get("/studio", response_class=HTMLResponse)
async def studio_page(request: Request, view: str = "overview") -> Response:
    if view not in VIEWS:
        raise HTTPException(404, "Partner page not found")
    try:
        studio = current(request)
    except HTTPException:
        return page(request, "expired.html", active_tab="partner")
    title, group = VIEWS[view]
    return page(
        request,
        "studio.html",
        active_tab="partner",
        studio=studio,
        view=view,
        view_title=title,
        group=group,
        views=VIEWS,
        ranked=rank_use_cases(studio.use_cases, studio.scoring_weights),
        weights=studio.scoring_weights,
        dimensions=list(Dimension),
        stages=list(Stage),
        sample_available=studio.id in PERSONAS and studio.fictional,
    )


@app.get("/studio/print", response_class=HTMLResponse)
async def print_plan(request: Request) -> Response:
    studio = current(request)
    return page(
        request,
        "print.html",
        studio=studio,
        active_tab="partner",
        ranked=rank_use_cases(studio.use_cases, studio.scoring_weights),
        weights=studio.scoring_weights,
        dimensions=list(Dimension),
    )


@app.post("/partners/{partner_id}/tasks/{task_id}")
async def update_task(
    request: Request, partner_id: str, task_id: str, update: TaskUpdate
) -> Response:
    token = request.cookies.get(COOKIE)
    if not token or not store.exists(token):
        raise HTTPException(410, "Session expired. Open the pipeline to start again.")
    if not store.update_task(token, partner_id, task_id, update.done):
        raise HTTPException(404, "Preparation task not found")
    response = JSONResponse({"saved": True})
    set_session_cookie(response, token, request)
    return response


@app.post("/partners/{partner_id}/tracking")
async def update_tracking(request: Request, partner_id: str, update: TrackingUpdate) -> Response:
    token = request.cookies.get(COOKIE)
    if not token or not store.exists(token):
        raise HTTPException(410, "Session expired. Open the pipeline to start again.")
    try:
        saved = store.update_tracking(token, partner_id, update)
    except ValidationError as error:
        raise HTTPException(422, "Counts cannot exceed the planned or invited totals.") from error
    if not saved:
        raise HTTPException(404, "Partner tracking not found")
    response = JSONResponse({"saved": True})
    set_session_cookie(response, token, request)
    return response


@app.post("/studio/weights")
async def update_weights(request: Request, update: WeightUpdate) -> Response:
    studio = current(request)
    try:
        rank_use_cases(studio.use_cases, update.weights)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    studio.scoring_weights = update.weights
    token = request.cookies.get(COOKIE)
    if token:
        store.put(token, studio)
    return Response(status_code=204)


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
    token, _ = workspace_token(request)
    try:
        store.put(token, studio)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    response = JSONResponse({"url": "/studio?view=overview"})
    set_session_cookie(response, token, request)
    return response


@app.post("/session/heartbeat")
async def heartbeat(request: Request) -> Response:
    if not store.exists(request.cookies.get(COOKIE)):
        raise HTTPException(410, "Session expired")
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
