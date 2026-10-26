from atelier import store as module
from atelier.store import IDLE_SECONDS, SessionStore, load_fixture


def test_idle_expiry_and_session_copy(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    now = [1.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: now[0])
    store = SessionStore()
    token = store.create(load_fixture("lena-voss"))
    retrieved = store.get(token)
    assert retrieved is not None
    retrieved.name = "Modified copy"
    again = store.get(token)
    assert again is not None and again.name == "Lena Voss"
    now[0] += IDLE_SECONDS - 1
    assert store.get(token) is not None  # Activity extends the idle deadline.
    now[0] += IDLE_SECONDS
    store.purge()
    assert store.get(token) is None
