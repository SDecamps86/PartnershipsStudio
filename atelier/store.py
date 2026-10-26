"""Session-isolated partner workspaces. No database or cross-visitor mutable state."""

import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from atelier.schemas import Studio
from atelier.tracking import TrackingUpdate

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
PERSONAS = ("lena-voss", "maison-aurelle", "juno-park", "circuit-vale", "oria-house-hotels")
IDLE_SECONDS = 1800
MAX_SESSIONS = 100
MAX_PARTNERS = 12
MAX_WORKSPACE_BYTES = 3_000_000


def load_fixture(persona: str, variant: str = "base") -> Studio:
    if persona not in PERSONAS or variant not in ("base", "sharpened"):
        raise ValueError("Unknown fictional example")
    return Studio.model_validate_json((FIXTURES / f"{persona}.{variant}.json").read_text())


@dataclass
class Session:
    studios: dict[str, Studio]
    active_id: str | None
    touched: float


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def clear(self) -> None:
        self._sessions.clear()

    def purge(self) -> None:
        cutoff = time.monotonic() - IDLE_SECONDS
        for token in list(self._sessions):
            if self._sessions[token].touched <= cutoff:
                del self._sessions[token]

    def _session(self, token: str | None) -> Session | None:
        self.purge()
        session = self._sessions.get(token or "")
        if session:
            session.touched = time.monotonic()
        return session

    def exists(self, token: str | None) -> bool:
        return self._session(token) is not None

    def create(self, studio: Studio | None = None) -> str:
        self.purge()
        if len(self._sessions) >= MAX_SESSIONS:
            oldest = min(self._sessions, key=lambda key: self._sessions[key].touched)
            del self._sessions[oldest]
        studios = {p: load_fixture(p) for p in PERSONAS}
        if studio:
            studios[studio.id] = studio.model_copy(deep=True)
        token = secrets.token_urlsafe(32)
        self._sessions[token] = Session(studios, studio.id if studio else None, time.monotonic())
        return token

    def get(self, token: str | None) -> Studio | None:
        session = self._session(token)
        if not session or session.active_id is None:
            return None
        return session.studios[session.active_id].model_copy(deep=True)

    def list(self, token: str) -> list[Studio]:
        session = self._session(token)
        return [s.model_copy(deep=True) for s in session.studios.values()] if session else []

    def select(self, token: str, partner_id: str) -> bool:
        session = self._session(token)
        if not session or partner_id not in session.studios:
            return False
        session.active_id = partner_id
        return True

    def put(self, token: str, studio: Studio, *, preserve_tracking: bool = False) -> bool:
        session = self._session(token)
        if session is None:
            return False
        if studio.id not in session.studios and len(session.studios) >= MAX_PARTNERS:
            raise ValueError(
                "This session holds at most 12 partners. Export and clear it to start over."
            )
        new = studio.model_copy(deep=True)
        existing = session.studios.get(studio.id)
        if preserve_tracking and existing:
            new.tracking = existing.tracking.model_copy(deep=True) if existing.tracking else None
            new.scoring_weights = existing.scoring_weights.copy()
        size = sum(
            len(s.model_dump_json().encode()) for key, s in session.studios.items() if key != new.id
        ) + len(new.model_dump_json().encode())
        if size > MAX_WORKSPACE_BYTES:
            raise ValueError("Session storage is full. Export and clear it before importing more.")
        session.studios[new.id] = new
        session.active_id = new.id
        return True

    def update_task(self, token: str, partner_id: str, task_id: str, done: bool) -> bool:
        session = self._session(token)
        studio = session.studios.get(partner_id) if session else None
        if not studio or not studio.tracking:
            return False
        for task in studio.tracking.tasks:
            if task.id == task_id:
                task.done = done
                studio.tracking.updated_by_user = True
                return True
        return False

    def update_tracking(self, token: str, partner_id: str, update: TrackingUpdate) -> bool:
        session = self._session(token)
        studio = session.studios.get(partner_id) if session else None
        if not studio or not studio.tracking:
            return False
        data = studio.tracking.model_dump()
        fields = update.model_dump()
        data["event"] = {
            **data["event"],
            "status": fields.pop("event_status"),
            "confirmed": fields.pop("confirmed"),
        }
        data.update(fields)
        data["updated_by_user"] = True
        studio.tracking = type(studio.tracking).model_validate(data)
        return True

    def delete(self, token: str | None) -> None:
        self._sessions.pop(token or "", None)
