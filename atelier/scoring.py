from collections.abc import Mapping

from atelier.schemas import Dimension, UseCase

DEFAULT_WEIGHTS: dict[Dimension, int] = dict(
    zip(Dimension, [25, 20, 20, 10, 10, 10, 5], strict=True)
)


def rank_use_cases(
    cases: list[UseCase], weights: Mapping[Dimension, int] | None = None
) -> list[tuple[UseCase, float]]:
    selected = DEFAULT_WEIGHTS if weights is None else weights
    if set(selected) != set(Dimension) or any(v < 0 or v > 100 for v in selected.values()):
        raise ValueError("Provide all seven weights, each from 0 to 100")
    total = sum(selected.values())
    if total == 0:
        raise ValueError("At least one weight must be positive")
    scored = [
        (u, sum(selected[d] * u.scores[d].score / 5 for d in Dimension) * 100 / total)
        for u in cases
    ]
    return sorted(
        scored,
        key=lambda pair: (
            -pair[1],
            -pair[0].scores[Dimension.risk_safety].score,
            pair[0].time_to_first_value_days,
            pair[0].id,
        ),
    )
