import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from atelier.implementation import Implementation
from atelier.store import PERSONAS, load_fixture
from scripts.build_demo import build


def test_every_partner_has_a_named_sa_and_six_functional_teams() -> None:
    for persona in PERSONAS:
        project = load_fixture(persona).implementation
        assert project is not None
        lead = next(member for member in project.team if member.id == project.sa_lead_id)
        assert lead.department == "Solutions architecture"
        assert project.fictional_team
        assert {m.department for m in project.team} == {
            "Sales",
            "Marketing",
            "Legal",
            "Solutions architecture",
            "Engineering",
            "Product",
        }
        assert len(project.milestones) == 5


def test_invalid_counts_dates_and_circular_dependencies_are_rejected() -> None:
    project = load_fixture("circuit-vale").implementation
    assert project is not None
    data = project.model_dump()
    data["seats_activated"] = data["seats_planned"] + 1
    with pytest.raises(ValidationError):
        Implementation.model_validate(data)
    data = project.model_dump()
    data["target_launch"] = "2000-01-01"
    with pytest.raises(ValidationError):
        Implementation.model_validate(data)
    data = project.model_dump()
    data["milestones"][0]["dependencies"] = ["m2"]
    with pytest.raises(ValidationError, match="cycle"):
        Implementation.model_validate(data)
    data = project.model_dump()
    data["sa_lead_id"] = "sales"
    with pytest.raises(ValidationError, match="solutions architect"):
        Implementation.model_validate(data)


def test_static_publication_contains_only_fictional_fixtures(tmp_path: Path) -> None:
    build(tmp_path)
    data = json.loads((tmp_path / "assets/data.json").read_text())
    assert len(data["base"]) == len(PERSONAS)
    assert all(p["fictional"] for p in data["base"])
    assert all(
        e["source_url"].startswith("fixture://") for p in data["base"] for e in p["evidence"]
    )
    html = (tmp_path / "index.html").read_text()
    assert "Demo version" in html
    assert "owner’s private environment" in html
    assert "Deployment &amp; enablement" in html or "Deployment & enablement" in html
    assert not (tmp_path / ".env").exists()
    assert not (tmp_path / "app").exists()
    script = (tmp_path / "assets/demo.js").read_text()
    assert "fetch('assets/data.json')" in script
    assert "fetch('assets/schema.json')" in script
    assert "OPENAI_API_KEY" not in script
