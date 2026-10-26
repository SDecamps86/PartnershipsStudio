"""M0 contract only; grounding and persona evaluation begins in M1."""

from fastapi.testclient import TestClient

from app.main import app


def test_honest_demo_shell() -> None:
    with TestClient(app) as client:
        html = client.get("/").text
        for text in [
            "Lena Voss",
            "Maison Aurelle",
            "Juno Park",
            "Fictional examples",
            "Verify before outreach",
            "arrives in M1",
            "Skip to content",
        ]:
            assert text in html
        assert "<script" not in html
        assert "disabled" in html
