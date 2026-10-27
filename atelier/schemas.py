"""Shared validated contracts for demo fixtures, imports and later pipeline stages."""

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from atelier.contracts import Model, Score, Text
from atelier.implementation import Implementation
from atelier.tracking import Tracking

Confidence = Literal["low", "medium", "high"]
Origin = Literal["research", "user", "assumption", "fixture"]


class Dimension(StrEnum):
    goal_fit = "goal_fit"
    audience_fit = "audience_fit"
    values_fit = "values_fit"
    time_to_first_value = "time_to_first_value"
    feasibility = "feasibility"
    differentiation = "differentiation"
    risk_safety = "risk_safety"


class Evidence(Model):
    id: Text
    claim: Text
    source_url: str
    source_title: Text
    date: date
    kind: Literal["work", "audience", "values", "business", "press", "risk"]
    origin: Origin


class Grounded(Model):
    statement: Text
    evidence_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence: Confidence = "medium"

    @model_validator(mode="after")
    def grounded(self) -> Self:
        if not self.evidence_ids and not self.assumptions:
            raise ValueError("A statement needs evidence or an explicit assumption")
        return self


class Priority(Grounded):
    why_it_matters_for_onboarding: Text


class Fit(Model):
    score: Score
    rationale: Text
    evidence_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class Indicators(Model):
    fit_scorecard: dict[str, Fit]
    why_now_signals: list[Grounded]
    audience_signals: list[Grounded]
    business_signals: list[Grounded]


class Audience(Model):
    who: Grounded
    platforms: list[str]
    size_signals: Grounded


class Profile(Model):
    summary: Grounded
    creative_goals: list[Grounded]
    audience: Audience
    values: list[Grounded]
    style_signature: Grounded
    workflow_signals: list[Grounded]
    constraints: list[Grounded]
    sensitivity_level: Literal["standard", "confidential", "high"]
    what_matters_most: list[Priority] = Field(min_length=5, max_length=5)
    key_indicators: Indicators
    unknowns: list[str]
    questions_to_ask: list[str]


class WorkflowStep(Model):
    id: Text
    name: Text
    owner_role: Text
    tools: list[str]
    pain_points: list[str]
    time_cost_signal: Text
    opportunity: Text
    capability_ids: list[str]
    human_judgment_to_protect: Text
    origin: Origin


class ScoreReason(Model):
    score: Score
    rationale: Text


class Risk(Model):
    type: Text
    severity: Literal["low", "medium", "high"]
    mitigation: Text


class UseCase(Model):
    id: str = Field(pattern=r"^[A-Za-z0-9-]{1,60}$")
    title: Text
    one_line: Text
    capability_ids: list[str]
    workflow_step_ids: list[str]
    goal_link: Text
    audience_link: Text
    values_link: Text
    scores: dict[Dimension, ScoreReason]
    rationale: Text
    risks: list[Risk] = Field(min_length=1)
    time_to_first_value_days: int = Field(ge=1, le=365)
    effort: Literal["low", "medium", "high"]
    evidence_ids: list[str]
    assumptions: list[str]
    first_experiment: Text

    @model_validator(mode="after")
    def complete(self) -> Self:
        if set(self.scores) != set(Dimension):
            raise ValueError("All seven scoring dimensions are required")
        if not self.evidence_ids and not self.assumptions:
            raise ValueError("Use case must have evidence or an assumption")
        return self


class Rejected(Model):
    title: Text
    reason: Text
    risk: Risk


class DemoVersions(Model):
    five_min: Text
    twenty_min: Text
    sixty_min_hands_on: Text


class Beat(Model):
    time: Text
    action: Text
    intended_feeling: Text
    talking_point: Text


class DemoPlan(Model):
    use_case_id: str
    concept: Text
    why_this_demo: Text
    versions: DemoVersions
    script_beats: list[Beat]
    sample_inputs: list[str]
    assets_needed: list[str]
    wow_moment: Text
    fallback_plan: Text
    what_not_to_show: list[str]
    success_signal: Text


class Discretion(Model):
    level: Text
    rules: list[str]


class DayBrief(Model):
    who: Text
    why_them: Text
    what_they_care_about: list[str]
    do: list[str]
    avoid: list[str]
    open_questions: list[str]
    next_step: Text


class EventPlan(Model):
    format: Text
    size: Text
    setting: Text
    run_of_show: list[Beat]
    room_design_notes: list[str]
    guest_brief_fields: list[str]


class ExperiencePlan(Model):
    tone_and_voice: Text
    host_and_channel: Text
    invitation_draft: Text
    setting_and_pacing: Text
    discretion: Discretion
    accessibility_notes: list[str]
    day_brief: DayBrief
    event_plan: EventPlan | None = None
    what_to_avoid: list[str]


class Stakeholder(Model):
    name_or_role: Text
    role_in_decision: Literal["sponsor", "champion", "evaluator", "blocker", "user"]
    what_they_care_about: Text
    engagement_approach: Text
    risk: Text
    origin: Literal["user", "research", "fixture"]


class JourneyStage(Model):
    name: Literal[
        "Introduction", "Education", "Experimentation", "Adoption", "Long-term engagement"
    ]
    goal: Text
    activities: list[str]
    owner_roles: list[str]
    partner_signal: Text
    exit_criteria: Text
    week_range: Text


class Experiment(Model):
    hypothesis: Text
    setup: Text
    steps: list[str]
    metric: Text
    success_threshold: Text
    timebox_days: int = Field(ge=1, le=90)
    decision_gate: Text
    risk: Risk


class Touchpoint(Model):
    day: int = Field(ge=1, le=90)
    purpose: Text
    owner: Text
    output: Text


class Message(Model):
    when: Text
    channel: Text
    draft: Text


class Cadence(Model):
    weekly_standup_agenda: list[str]
    channel_setup: Text
    touchpoints_90_days: list[Touchpoint]
    follow_up_messages: list[Message]
    handover_checklist: list[str]


class FeedbackLoop(Model):
    capture_template: list[str]
    routing: Text
    close_the_loop_message: Text


class Metrics(Model):
    stage_definitions: dict[str, str]
    leading_indicators: list[str]
    time_to_activation_target: Text


class Flag(Model):
    section: Text
    severity: Literal["low", "medium", "high"]
    issue: Text
    suggested_fix: Text


class Context(Model):
    company: dict[str, str] = Field(default_factory=dict)
    role_department: dict[str, str] = Field(default_factory=dict)
    people: list[dict[str, str]] = Field(default_factory=list, max_length=8)
    event: dict[str, str] = Field(default_factory=dict)
    workflow: dict[str, str] = Field(default_factory=dict)
    history_goals: dict[str, str] = Field(default_factory=dict)
    notes: str = ""
    provenance: dict[str, Origin] = Field(default_factory=dict)
    layer_enabled: dict[str, bool] = Field(default_factory=dict)
    version: int = Field(default=0, ge=0)


class Change(Model):
    section: Text
    before: Text
    after: Text
    reason: Text


class Studio(Model):
    schema_version: Literal["1.0"] = "1.0"
    id: str = Field(pattern=r"^[a-z0-9-]{1,60}$")
    name: Text
    partner_type: Literal["solo artist", "brand", "creator", "studio", "institution"]
    fictional: bool
    variant: Literal["base", "sharpened"]
    relationship: Text
    confidence: Confidence
    scoring_weights: dict[Dimension, Annotated[int, Field(ge=0, le=100)]] = Field(
        default_factory=lambda: dict(zip(Dimension, [25, 20, 20, 10, 10, 10, 5], strict=True))
    )
    evidence: list[Evidence] = Field(max_length=25)
    profile: Profile
    workflow: list[WorkflowStep]
    use_cases: list[UseCase] = Field(min_length=10, max_length=10)
    not_recommended: list[Rejected]
    demo: DemoPlan
    experience: ExperiencePlan
    stakeholders: list[Stakeholder]
    journey: list[JourneyStage] = Field(min_length=5, max_length=5)
    experiments: list[Experiment] = Field(min_length=3, max_length=3)
    cadence: Cadence
    feedback: FeedbackLoop
    metrics: Metrics
    flags: list[Flag]
    claims_audit: list[str]
    context_conflicts: list[str]
    context: Context
    changes: list[Change] = Field(default_factory=list)
    tracking: Tracking | None = None
    implementation: Implementation | None = None

    @model_validator(mode="after")
    def references(self) -> Self:
        if set(self.scoring_weights) != set(Dimension) or sum(self.scoring_weights.values()) == 0:
            raise ValueError("All seven weights are required and at least one must be positive")
        ids = [e.id for e in self.evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("Evidence IDs must be unique")
        uc_ids = [u.id for u in self.use_cases]
        if len(uc_ids) != len(set(uc_ids)) or self.demo.use_case_id not in uc_ids:
            raise ValueError("Use case IDs must be unique; demo must reference a use case")
        expected = [
            "Introduction",
            "Education",
            "Experimentation",
            "Adoption",
            "Long-term engagement",
        ]
        if [s.name for s in self.journey] != expected:
            raise ValueError("Journey must contain the five ordered stages")
        workflow_ids = {s.id for s in self.workflow}
        for u in self.use_cases:
            if not set(u.workflow_step_ids) <= workflow_ids:
                raise ValueError("Unknown workflow step")
        if self.tracking:
            refs = self.tracking.critical_evidence_ids + self.tracking.workflow_evidence_ids
            if not set(refs) <= set(ids):
                raise ValueError("Tracking references unknown evidence")
        self._check_evidence(self.model_dump(), set(ids))
        return self

    @staticmethod
    def _check_evidence(value: object, ids: set[str]) -> None:
        if isinstance(value, dict):
            refs = value.get("evidence_ids", [])
            if not set(refs) <= ids:
                raise ValueError("Unknown evidence reference")
            for child in value.values():
                Studio._check_evidence(child, ids)
        elif isinstance(value, list):
            for child in value:
                Studio._check_evidence(child, ids)


class WeightUpdate(Model):
    weights: dict[Dimension, Annotated[int, Field(ge=0, le=100)]]
