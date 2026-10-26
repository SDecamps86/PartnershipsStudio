import json

import pytest
from fastapi.testclient import TestClient

from app.main import VIEWS, app
from atelier.settings import Settings
from atelier.store import PERSONAS, load_fixture

ORIGIN = {"origin": "http://testserver"}


def test_pages_and_security() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "milestone": "M1"}
        for path in ["/", "/status", "/privacy", "/report"]:
            response = client.get(path)
            assert response.status_code == 200
            assert response.headers["x-robots-tag"] == "noindex, nofollow"
            assert response.headers["cache-control"] == "no-store"
            assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert client.get("/docs").status_code == 404
        assert not Settings(app_mode="live").live_available


@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("variant", ["base", "sharpened"])
def test_all_twelve_sections_and_exports(persona: str, variant: str) -> None:
    with TestClient(app) as client:
        response = client.get(f"/examples/{persona}/{variant}")
        assert response.status_code == 200
        full = client.get("/studio/print")
        for view in VIEWS:
            assert client.get("/studio", params={"view": view}).status_code == 200
        for section in [
            "overview",
            "priorities",
            "use-cases",
            "workflow",
            "demo",
            "experience",
            "stakeholders",
            "journey",
            "experiments",
            "cadence",
            "feedback",
            "integrity",
        ]:
            assert f'id="{section}"' in full.text
        data = client.get("/studio/export/json")
        assert data.status_code == 200
        assert data.json() == load_fixture(persona, variant).model_dump(mode="json")
        markdown = client.get("/studio/export/md")
        assert markdown.status_code == 200
        assert "Ranked use cases" in markdown.text
        assert "Human Judgment To Protect" in markdown.text
        assert "What Matters Most" in markdown.text


def test_import_roundtrip_isolation_clear_and_security() -> None:
    fixture = load_fixture("lena-voss").model_dump(mode="json")
    fixture["name"] = '<script>alert("unsafe")</script>'
    payload = json.dumps(fixture)
    with TestClient(app) as one, TestClient(app) as two:
        assert one.post("/studio/import", content=payload).status_code == 403
        response = one.post("/studio/import", content=payload, headers=ORIGIN)
        assert response.status_code == 200
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "SameSite=strict" in response.headers["set-cookie"]
        html = one.get("/studio").text
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html
        assert two.get("/studio/data").status_code == 410
        assert one.get("/studio/data").json()["name"] == fixture["name"]
        assert one.post("/session/clear", headers=ORIGIN).status_code == 200
        assert one.get("/studio/data").status_code == 410


def test_bad_import_does_not_replace_active_studio() -> None:
    with TestClient(app) as client:
        client.get("/examples/juno-park/base")
        assert client.post("/studio/import", content=b"{", headers=ORIGIN).status_code == 422
        assert (
            client.post("/studio/import", content=b"x" * 512001, headers=ORIGIN).status_code == 413
        )
        assert client.get("/studio/data").json()["name"] == "Juno Park"
        assert client.get("/examples/missing/base").status_code == 404
        assert client.get("/examples/lena-voss/missing").status_code == 404
        assert client.get("/studio/export/exe").status_code == 404


def test_export_preserves_custom_weights() -> None:
    from atelier.schemas import Dimension

    weights = dict.fromkeys(Dimension, 0)
    weights[Dimension.risk_safety] = 100
    with TestClient(app) as client:
        client.get("/examples/lena-voss/base")
        response = client.get("/studio/export/json", params={"weights": json.dumps(weights)})
        assert response.status_code == 200
        assert response.json()["scoring_weights"] == weights
        client.post("/studio/import", content=response.content, headers=ORIGIN)
        assert client.get("/studio/data").json()["scoring_weights"] == weights
        assert 'value="100"' in client.get("/studio?view=use-cases").text
        assert client.get("/studio/export/json", params={"weights": "{}"}).status_code == 400
