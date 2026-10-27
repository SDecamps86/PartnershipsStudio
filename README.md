# PartnershipsStudio

An internal workflow demonstrated with fictional partner data: preparation, pipeline management, customer deployment and enablement.

The current entry point has four tabs: **Prepare**, **Pipeline**, **Partner**, and **Deployment & enablement**. A visible notice explains that this is a demo and that the working version and operational data belong to the owner's private environment. That owner-environment statement was supplied by the owner; this build does not access it.

## Interactive demo

Visitors can edit partner context, event details, lead status, metric targets/counts, workflow steps, use cases/scores, priorities and preparation tasks. Implementation projects include a dedicated solutions architect, dated milestones and dependencies, rollout progress, blockers, training/seat indicators, and fictional owners in Sales, Marketing, Legal, Solutions Architecture, Engineering and Product.

Edits remain in browser memory and are lost on reload. Export one partner or the complete workspace as JSON to retain them; import restores validated data. No edit or import is sent to an owner system or server. Only the theme preference uses localStorage. Editing context does not silently regenerate recommendations.

All five partners, team names, dates and operating counts are fictional. Readiness measures checklist completion; implementation progress is the mean milestone completion; activation and training counts are manually supplied demo indicators.

## Run

```sh
uv sync --frozen
make run
```

Open http://127.0.0.1:8000. `make run` builds the static demo before starting FastAPI. The Python API and original server-rendered views remain as a local foundation. They are not included in the static publication package.

```sh
make check
make eval
PYTHONPATH=. uv run python scripts/build_demo.py --output site/dist
```

Static output can be served by any static host. The build accepts only the known fictional fixture files; it never reads sessions, environment secrets or owner data. The demo needs no API key, generation endpoint, analytics, database or JavaScript build step.

## Walkthrough and publication

A 45-second silent, captioned interface walkthrough is included at `site/assets/mini-demo.mp4`, with a poster and WebVTT captions. It is available through Watch demo in the app. It is an annotated sequence of actual interface captures, not a real customer recording.

The requested publication was attempted through Sites. Registration succeeded; source submission was blocked by the desktop execution approval policy before a version could be pushed/deployed. See [publication status](docs/PUBLISH_STATUS.md) and [verification](evals/reports/DEPLOYMENT_DEMO.md).

[Architecture](docs/ARCHITECTURE.md) · [Decisions](docs/DECISIONS.md) · [Privacy](docs/PRIVACY.md) · [Deployment](docs/DEPLOY.md)

MIT licensed. Fictional examples imply no affiliation or endorsement.
