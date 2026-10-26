# PartnershipsStudio

An internal tool for tailoring partner experiences and tracking their preparation.

## Three working tabs

- **Prepare:** enter a partner or client name. The demo opens five fictional partners.
- **Pipeline:** see partner stages, pending actions, session readiness, upcoming experiences and the complete directory. Filter by name, workflow, stage, preparation state or audience; switch between list and board views.
- **Partner:** open a concise operational overview, then use focused pages for context, workflow, use cases, session design, the host brief, journey, experiments, follow-up, tasks and sources. Only the selected page is rendered.

The overview puts identity, lead maturity, importance, business context, a specific workflow, next event and audience alongside readiness, touchpoints, pilots and independent use. Preparation checkboxes update readiness and the pipeline. Update tracking changes stage, maturity, priority, invitation status and observed-count fields. All supplied figures and events are fictional examples, not actual business results.

## Run locally

```sh
uv sync --frozen
make check
make run
```

Open http://127.0.0.1:8000. Python 3.12+ and uv are required. No API key or AI call is used. The runtime uses local assets only and has no JavaScript build step.

## Demo partners

| Fictional partner | Preparation focus |
| --- | --- |
| Lena Voss | Automotive 3D client reviews, craft authorship and NDA boundaries |
| Maison Aurelle | Luxury fashion storytelling, regional localization and approval ownership |
| Juno Park | Listening, creative boundaries and fan trust before a demo |
| Circuit Vale | Fashion technology, digital-to-physical sample handoffs and tested product claims |
| Oria House Hotels | Luxury hospitality, property-host handoffs and accurate service promises without guest data |

Each has a base plan and a prewritten sample-context version, ten scored use cases, all twelve original content sections, three experiments and a five-stage journey. Recommendations cite fictional brief evidence or identify assumptions.

## Saving and retention

Partner selection preserves the workspace's task and tracking changes. Sample-context switching replaces the prepared content while keeping operational tracking and score weights. Scoring weights also survive navigation between partner pages.

Export the current partner as JSON to preserve its complete plan, weights and tracking. Markdown, section copying and print views are available too. Restore JSON through the pipeline's Import control. Browser storage holds only the theme preference. The workspace is session-only, expires after 30 idle minutes, and disappears on server restart. Clear workspace removes all current session data; reopening the pipeline seeds fresh fictional examples. There is no cross-session CRM or external integration.

## Current limits

M1 plus the requested UX/pipeline revision. Live research and generation remain M2; free-form context, general inline content editing, verification, locks and comparison remain M3. Private deployment, access codes, spend protection and public static showcase remain M4. No remote push or deployment has occurred.

Scores, dates, counts and thresholds are planning examples or operator-entered values. Readiness means preparation checklist completion, not lead conversion likelihood or confirmed attendance. Independent use is a manually recorded count, not product telemetry. Verify before real outreach. Print pagination depends on the browser/printer.

[Architecture](docs/ARCHITECTURE.md) · [Decisions](docs/DECISIONS.md) · [Privacy](docs/PRIVACY.md) · [Deployment](docs/DEPLOY.md) · [UX verification](evals/reports/UX.md)

MIT licensed. Fictional data implies no affiliation or endorsement.
