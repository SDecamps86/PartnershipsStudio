"""Fictional customer implementation plans shared by local and published demos."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from atelier.contracts import Model, Text


class ProjectMember(Model):
    id: str = Field(pattern=r"^[a-z0-9-]{1,40}$")
    name: Text
    department: Literal[
        "Sales", "Marketing", "Legal", "Solutions architecture", "Engineering", "Product"
    ]
    role: Text
    responsibility: Text


class Milestone(Model):
    id: str = Field(pattern=r"^[a-z0-9-]{1,40}$")
    title: Text
    phase: Literal["Discovery", "Solution design", "Pilot", "Rollout", "Adoption"]
    start: date
    due: date
    progress: int = Field(ge=0, le=100)
    owner_id: str
    dependencies: list[str] = Field(default_factory=list)
    exit_criteria: Text
    status: Literal["Planned", "In progress", "Complete", "Blocked"]

    @model_validator(mode="after")
    def consistency(self) -> Self:
        if self.due < self.start:
            raise ValueError("Milestone due date precedes start")
        if (self.status == "Complete") != (self.progress == 100):
            raise ValueError("Complete milestones must have 100% progress")
        return self


class Implementation(Model):
    title: Text
    objective: Text
    solution_workflow: Text
    phase: Literal["Discovery", "Solution design", "Pilot", "Rollout", "Adoption"]
    health: Literal["On track", "At risk", "Blocked"]
    sa_lead_id: str
    customer_lead: Text
    kickoff: date
    target_launch: date
    next_checkpoint: date
    environment: Text
    success_criteria: list[str] = Field(min_length=1, max_length=10)
    team: list[ProjectMember] = Field(min_length=6, max_length=16)
    milestones: list[Milestone] = Field(min_length=1, max_length=20)
    seats_planned: int = Field(ge=1, le=100000)
    seats_activated: int = Field(ge=0, le=100000)
    training_planned: int = Field(ge=1, le=1000)
    training_delivered: int = Field(ge=0, le=1000)
    users_to_train: int = Field(ge=1, le=100000)
    users_trained: int = Field(ge=0, le=100000)
    blockers: list[str] = Field(default_factory=list, max_length=12)
    next_action: Text
    notes: str = Field(default="", max_length=8000)
    fictional_team: Literal[True] = True
    updated_by_user: bool = False

    @model_validator(mode="after")
    def consistency(self) -> Self:
        ids = {member.id for member in self.team}
        milestone_ids = {item.id for item in self.milestones}
        if len(ids) != len(self.team) or len(milestone_ids) != len(self.milestones):
            raise ValueError("Team and milestone IDs must be unique")
        lead = next((m for m in self.team if m.id == self.sa_lead_id), None)
        if not lead or lead.department != "Solutions architecture":
            raise ValueError("A dedicated solutions architect must lead implementation")
        for item in self.milestones:
            if item.owner_id not in ids or not set(item.dependencies) <= milestone_ids:
                raise ValueError("Unknown milestone owner or dependency")
            if item.id in item.dependencies:
                raise ValueError("A milestone cannot depend on itself")
        graph = {item.id: item.dependencies for item in self.milestones}
        visited: set[str] = set()
        active: set[str] = set()

        def visit(key: str) -> None:
            if key in active:
                raise ValueError("Milestone dependencies contain a cycle")
            if key in visited:
                return
            active.add(key)
            for dependency in graph[key]:
                visit(dependency)
            active.remove(key)
            visited.add(key)

        for key in graph:
            visit(key)
        if self.target_launch < self.kickoff:
            raise ValueError("Launch cannot precede kickoff")
        if self.seats_activated > self.seats_planned:
            raise ValueError("Activated seats exceed planned seats")
        if (
            self.training_delivered > self.training_planned
            or self.users_trained > self.users_to_train
        ):
            raise ValueError("Training completion exceeds plan")
        return self
