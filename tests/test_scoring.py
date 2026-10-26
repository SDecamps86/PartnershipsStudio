import pytest
from pydantic import ValidationError

from atelier.schemas import Dimension, Studio
from atelier.scoring import DEFAULT_WEIGHTS, rank_use_cases
from atelier.store import load_fixture


def test_weights_and_deterministic_ties() -> None:
    cases = load_fixture("lena-voss").use_cases
    case = cases[0].model_copy(deep=True)
    twin = case.model_copy(deep=True)
    twin.id = "tie"
    twin.time_to_first_value_days = 1
    case.time_to_first_value_days = 2
    assert rank_use_cases([case, twin])[0][0].id == "tie"
    expected = sum(DEFAULT_WEIGHTS[d] * cases[0].scores[d].score / 5 for d in Dimension)
    assert dict((u.id, s) for u, s in rank_use_cases(cases))[cases[0].id] == expected
    risk_only = dict.fromkeys(Dimension, 0)
    risk_only[Dimension.risk_safety] = 100
    ranked = rank_use_cases(cases, risk_only)
    assert ranked[0][0].scores[Dimension.risk_safety].score == 5
    assert ranked[0][1] == 100
    with pytest.raises(ValueError):
        rank_use_cases(cases, dict.fromkeys(Dimension, 0))


def test_schema_rejects_missing_evidence_and_incomplete_scores() -> None:
    data = load_fixture("lena-voss").model_dump(mode="json")
    data["use_cases"][0]["evidence_ids"] = ["DOES-NOT-EXIST"]
    with pytest.raises(ValidationError):
        Studio.model_validate(data)
    data = load_fixture("lena-voss").model_dump(mode="json")
    del data["use_cases"][0]["scores"]["goal_fit"]
    with pytest.raises(ValidationError):
        Studio.model_validate(data)
