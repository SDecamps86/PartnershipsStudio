"""Offline quality gates: actual evidence, distinct plans and reversible fixture previews."""

import json
from pathlib import Path

from atelier.scoring import DEFAULT_WEIGHTS, rank_use_cases
from atelier.store import PERSONAS, load_fixture


def test_all_fixture_contracts_and_capabilities() -> None:
    root = Path(__file__).resolve().parent.parent
    profile = json.loads((root / "config/platform.example.json").read_text())
    approved = {cap["id"] for cap in profile["approved_capabilities"]}
    for persona in PERSONAS:
        for variant in ("base", "sharpened"):
            studio = load_fixture(persona, variant)
            assert studio.fictional
            assert len(studio.profile.what_matters_most) == 5
            assert len(studio.journey) == 5
            assert len(studio.experiments) == 3
            assert len(studio.use_cases) == 10
            assert studio.not_recommended
            assert all(u.evidence_ids or u.assumptions for u in studio.use_cases)
            assert all(u.risks and all(r.mitigation for r in u.risks) for u in studio.use_cases)
            assert all(set(u.capability_ids) <= approved for u in studio.use_cases)
            assert all("because" in u.rationale.lower() for u in studio.use_cases)
            assert all(e.source_url.startswith("fixture://") for e in studio.evidence)
            assert studio.cadence.touchpoints_90_days[-1].day == 90


def test_tailoring_and_juno_boundaries() -> None:
    tops = [rank_use_cases(load_fixture(p).use_cases)[0][0].title for p in PERSONAS]
    assert len(set(tops)) == len(PERSONAS)
    juno = load_fixture("juno-park")
    assert "listening" in tops[2].lower()
    assert "no demonstration" in juno.demo.concept.lower()
    assert len(juno.not_recommended) >= 3
    assert any(f.severity == "high" for f in juno.flags)


def test_sample_context_preview_is_reversible_and_idempotent() -> None:
    for p in PERSONAS:
        base = load_fixture(p)
        sharp = load_fixture(p, "sharpened")
        assert sharp.model_dump() == load_fixture(p, "sharpened").model_dump()
        assert base.model_dump() == load_fixture(p, "base").model_dump()
        assert rank_use_cases(base.use_cases)[0][0].id != rank_use_cases(sharp.use_cases)[0][0].id
        assert all(c.reason for c in sharp.changes)
        assert sharp.context.layer_enabled
    # This checks precomputed variants only, not M3's free-form layer recomputation.


def test_scores_match_formula() -> None:
    for persona in PERSONAS:
        for case, score in rank_use_cases(load_fixture(persona).use_cases):
            expected = sum(DEFAULT_WEIGHTS[d] * case.scores[d].score / 5 for d in DEFAULT_WEIGHTS)
            assert abs(score - expected) < 1e-9


def test_tracking_and_funnel_consistency() -> None:
    from datetime import date

    from atelier.pipeline import dashboard

    studios = [load_fixture(p) for p in PERSONAS]
    data = dashboard(studios, date(2026, 10, 26))
    assert sum(data["stage_counts"].values()) == len(PERSONAS)
    assert sum(data["counts"].values()) == len(PERSONAS)
    assert data["pending_tasks"] == sum(
        len(s.tracking.tasks) - s.tracking.completed for s in studios if s.tracking
    )
    assert all(
        s.tracking and s.tracking.event.confirmed <= s.tracking.event.invited for s in studios
    )
