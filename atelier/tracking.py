"""Small session-only preparation tracker; no CRM or external synchronization."""

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from atelier.contracts import Model, Text


class Stage(StrEnum):
    introduction = "Introduction"
    education = "Education"
    experimentation = "Experimentation"
    adoption = "Adoption"
    engagement = "Long-term engagement"


class Task(Model):
    id: str = Field(pattern=r"^[a-z0-9-]{1,50}$")
    title: Text
    owner: Text
    due: date
    done: bool = False
    category: Literal["qualification", "invitation", "assets", "approval", "follow-up"]


class PlannedEvent(Model):
    title: Text
    date: date
    time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    duration_minutes: int = Field(ge=5, le=480)
    format: Text
    venue: Text
    audience: Text
    invited: int = Field(ge=0, le=10000)
    confirmed: int = Field(ge=0, le=10000)
    status: Literal["Not invited", "Invitation drafted", "Invited", "Confirmed", "Completed"]

    @model_validator(mode="after")
    def counts(self) -> Self:
        if self.confirmed > self.invited:
            raise ValueError("Confirmed attendance cannot exceed invited attendance")
        return self


class Tracking(Model):
    sector: Text
    initials: str = Field(min_length=1, max_length=4)
    owner: Text
    stage: Stage
    maturity: Literal["Unqualified", "Qualifying", "Qualified", "Active"]
    priority: Literal["High", "Medium", "Low"]
    business_context: Text
    why_critical: Text
    critical_evidence_ids: list[str] = Field(default_factory=list)
    current_workflow: Text
    workflow_evidence_ids: list[str] = Field(default_factory=list)
    workflow_origin: Literal["fixture", "assumption", "user"] = "fixture"
    audience_segment: Text
    event: PlannedEvent
    tasks: list[Task] = Field(max_length=30)
    touchpoints_completed: int = Field(ge=0, le=1000)
    touchpoints_planned: int = Field(ge=1, le=1000)
    pilots_completed: int = Field(ge=0, le=1000)
    pilots_planned: int = Field(ge=1, le=1000)
    independent_uses: int = Field(ge=0, le=10000)
    activation_target_days: int = Field(ge=1, le=365)
    origin: Literal["fixture", "user"] = "fixture"
    updated_by_user: bool = False

    @model_validator(mode="after")
    def task_ids(self) -> Self:
        if len({t.id for t in self.tasks}) != len(self.tasks):
            raise ValueError("Task IDs must be unique")
        if self.touchpoints_completed > self.touchpoints_planned:
            raise ValueError("Completed touchpoints exceed plan")
        if self.pilots_completed > self.pilots_planned:
            raise ValueError("Completed pilots exceed plan")
        return self

    @property
    def completed(self) -> int:
        return sum(task.done for task in self.tasks)

    @property
    def readiness(self) -> int:
        return round(100 * self.completed / len(self.tasks)) if self.tasks else 0

    @property
    def state(self) -> str:
        if self.tasks and self.completed == len(self.tasks):
            return "Ready"
        return "In progress" if self.completed else "Pending"

    @property
    def next_task(self) -> Task | None:
        pending = sorted((task for task in self.tasks if not task.done), key=lambda task: task.due)
        return pending[0] if pending else None


class TrackingUpdate(Model):
    stage: Stage
    maturity: Literal["Unqualified", "Qualifying", "Qualified", "Active"]
    priority: Literal["High", "Medium", "Low"]
    event_status: Literal["Not invited", "Invitation drafted", "Invited", "Confirmed", "Completed"]
    confirmed: Annotated[int, Field(ge=0, le=10000)]
    touchpoints_completed: int = Field(ge=0, le=1000)
    pilots_completed: int = Field(ge=0, le=1000)
    independent_uses: int = Field(ge=0, le=10000)


class TaskUpdate(Model):
    done: bool
