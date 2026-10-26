"""Short-lived, process-local sessions. Never cache visitor data across sessions."""

import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from atelier.schemas import Studio

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
PERSONAS = ("lena-voss", "maison-aurelle", "juno-park")
IDLE_SECONDS = 1800
MAX_SESSIONS = 200


def load_fixture(persona: str, variant: str = "base") -> Studio:
    if persona not in PERSONAS or variant not in ("base", "sharpened"):
        raise ValueError("Unknown fictional example")
    return Studio.model_validate_json((FIXTURES / f"{persona}.{variant}.json").read_text())


@dataclass
class Session:
    studio: Studio
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

    def create(self, studio: Studio) -> str:
        self.purge()
        if len(self._sessions) >= MAX_SESSIONS:
            oldest = min(self._sessions, key=lambda key: self._sessions[key].touched)
            del self._sessions[oldest]
        token = secrets.token_urlsafe(32)
        self._sessions[token] = Session(studio.model_copy(deep=True), time.monotonic())
        return token

    def get(self, token: str | None) -> Studio | None:
        self.purge()
        session = self._sessions.get(token or "")
        if session is None:
            return None
        session.touched = time.monotonic()
        return session.studio.model_copy(deep=True)

    def delete(self, token: str | None) -> None:
        self._sessions.pop(token or "", None)
