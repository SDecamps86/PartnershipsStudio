"""Dashboard aggregation from session records; no estimated conversion rates."""

from datetime import date
from typing import Any

from atelier.schemas import Studio
from atelier.tracking import Stage


def dashboard(
    studios: list[Studio],
    today: date,
    query: str = "",
    stage: str = "",
    state: str = "",
    priority: str = "",
    audience: str = "",
) -> dict[str, Any]:
    tracked = [s for s in studios if s.tracking is not None]
    filtered = []
    for studio in studios:
        t = studio.tracking
        haystack = " ".join(
            [
                studio.name,
                t.sector if t else "",
                t.audience_segment if t else "",
                t.current_workflow if t else "",
            ]
        ).casefold()
        if query.casefold() not in haystack:
            continue
        if stage and (not t or t.stage != stage):
            continue
        if state and (not t or t.state != state):
            continue
        if priority and (not t or t.priority != priority):
            continue
        if audience and (not t or t.audience_segment != audience):
            continue
        filtered.append(studio)
    events = sorted(
        (
            s
            for s in tracked
            if s.tracking
            and s.tracking.event.date >= today
            and s.tracking.event.status != "Completed"
        ),
        key=lambda s: s.tracking.event.date if s.tracking else date.max,
    )
    attention = sorted(
        [(s, task) for s in tracked if s.tracking for task in s.tracking.tasks if not task.done],
        key=lambda pair: (pair[1].due, pair[0].name),
    )
    counts = {
        name: sum(s.tracking.state == name for s in tracked if s.tracking)
        for name in ["Pending", "In progress", "Ready"]
    }
    stages = {
        name.value: sum(s.tracking.stage == name for s in tracked if s.tracking) for name in Stage
    }
    return dict(
        partners=filtered,
        total=len(studios),
        tracked_total=len(tracked),
        counts=counts,
        pending_tasks=len(attention),
        upcoming=events[:3],
        attention=attention[:4],
        stage_counts=stages,
        max_stage_count=max(stages.values(), default=1) or 1,
        activated=sum(s.tracking.independent_uses > 0 for s in tracked if s.tracking),
        audiences=sorted({s.tracking.audience_segment for s in tracked if s.tracking}),
        query=query,
        stage=stage,
        state=state,
        priority=priority,
        audience=audience,
        today=today,
    )
