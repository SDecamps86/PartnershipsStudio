from fastapi.testclient import TestClient

from app.main import app
from atelier.settings import Settings


def test_pages_and_security() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "milestone": "M0"}
        for path in ["/", "/status", "/privacy", "/report"]:
            response = client.get(path)
            assert response.status_code == 200
            assert response.headers["x-robots-tag"] == "noindex, nofollow"
            assert response.headers["cache-control"] == "no-store"
            assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
            assert "set-cookie" not in response.headers


def test_live_cannot_be_enabled() -> None:
    assert not Settings(app_mode="live").live_available
    with TestClient(app) as client:
        assert client.post("/generate", json={"name": "Example"}).status_code == 404
        assert client.get("/docs").status_code == 404


def test_local_styles() -> None:
    with TestClient(app) as client:
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "prefers-color-scheme:dark" in response.text
