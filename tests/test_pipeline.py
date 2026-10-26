from fastapi.testclient import TestClient

from app.main import app
from atelier.store import PERSONAS

ORIGIN = {"origin": "http://testserver"}


def test_prepare_is_only_intake_and_dashboard_has_five_partners() -> None:
    with TestClient(app) as client:
        home = client.get("/").text
        assert "Prepare a partner experience" in home
        assert "partner-form" in home
        assert "example-card" not in home
        assert "metric-card" not in home
        assert "import-file" not in home
        dashboard = client.get("/pipeline").text
        for name in [
            "Lena Voss",
            "Maison Aurelle",
            "Juno Park",
            "Circuit Vale",
            "Oria House Hotels",
        ]:
            assert name in dashboard
        assert "Needs attention" in dashboard
        assert "Upcoming experiences" in dashboard
        assert "All partners" in dashboard
        assert "pipeline-board" in client.get("/pipeline?layout=board").text
        assert "Select a partner" in client.get("/studio").text


def test_partner_tabs_only_render_selected_content() -> None:
    with TestClient(app) as client:
        overview = client.get("/partners/circuit-vale").text
        assert "Who is this partner?" in overview
        assert "Next experience" in overview
        assert "Why this partner matters" in overview
        assert "Specific workflow" in overview
        assert "Session readiness" in overview
        assert 'id="use-cases"' not in overview
        cases = client.get("/studio?view=use-cases").text
        assert 'id="use-cases"' in cases
        assert 'id="journey"' not in cases
        assert 'id="cadence"' not in cases
        assert client.get("/studio?view=missing").status_code == 404


def test_task_updates_persist_across_partners_and_are_session_isolated() -> None:
    with TestClient(app) as one, TestClient(app) as two:
        one.get("/pipeline")
        two.get("/pipeline")
        one.get("/partners/juno-park")
        task_url = "/partners/juno-park/tasks/consent"
        assert one.post(task_url, json={"done": True}).status_code == 403
        assert one.post(task_url, json={"done": True}, headers=ORIGIN).status_code == 200
        assert one.get("/studio/data").json()["tracking"]["tasks"][0]["done"] is True
        one.get("/partners/lena-voss")
        one.get("/partners/juno-park")
        assert one.get("/studio/data").json()["tracking"]["tasks"][0]["done"] is True
        two.get("/partners/juno-park")
        assert two.get("/studio/data").json()["tracking"]["tasks"][0]["done"] is False
        # Switching base/sharpened plans must not reset operational progress.
        one.get("/examples/juno-park/sharpened")
        assert one.get("/studio/data").json()["tracking"]["tasks"][0]["done"] is True
        assert one.post(task_url, json={"done": False}, headers=ORIGIN).status_code == 200
        assert one.get("/studio/data").json()["tracking"]["tasks"][0]["done"] is False


def test_tracking_validation_filters_and_saved_weights() -> None:
    with TestClient(app) as client:
        client.get("/partners/oria-house-hotels")
        before = client.get("/studio/data").json()["tracking"]
        update = dict(
            stage="Education",
            maturity="Qualified",
            priority="High",
            event_status="Confirmed",
            confirmed=5,
            touchpoints_completed=2,
            pilots_completed=1,
            independent_uses=1,
        )
        assert (
            client.post(
                "/partners/oria-house-hotels/tracking", json=update, headers=ORIGIN
            ).status_code
            == 200
        )
        data = client.get("/studio/data").json()["tracking"]
        assert data["stage"] == "Education"
        assert data["event"]["confirmed"] == 5
        assert data["updated_by_user"]
        update["confirmed"] = 100
        assert (
            client.post(
                "/partners/oria-house-hotels/tracking", json=update, headers=ORIGIN
            ).status_code
            == 422
        )
        assert client.get("/studio/data").json()["tracking"]["event"]["confirmed"] == 5
        assert before["event"]["confirmed"] == 2
        weights = client.get("/studio/data").json()["scoring_weights"]
        weights["risk_safety"] = 100
        assert (
            client.post("/studio/weights", json={"weights": weights}, headers=ORIGIN).status_code
            == 204
        )
        client.get("/partners/lena-voss")
        client.get("/partners/oria-house-hotels")
        assert client.get("/studio/data").json()["scoring_weights"]["risk_safety"] == 100
        filtered = client.get("/pipeline?q=Oria").text
        assert "/partners/oria-house-hotels" in filtered
        # The upcoming panel can include other partners; verify just the filtered directory.
        directory = filtered.split('id="partner-list"', 1)[1].split("dashboard-columns", 1)[0]
        assert "/partners/lena-voss" not in directory
        assert "/partners/oria-house-hotels" in directory
        assert "No partners match" in client.get("/pipeline?q=nonexistent").text
        assert len(PERSONAS) == 5
