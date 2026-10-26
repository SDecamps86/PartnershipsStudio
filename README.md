# PartnershipsStudio

An internal workspace for preparing partner sessions and follow-up.

**M1 — demo mode complete.** Open one of three fictional partners to review goals, use cases, workflow assumptions, demo preparation, experience design, stakeholders, a five-stage journey, three experiments, a 90-day cadence, feedback, metrics and sources.

```sh
uv sync --frozen
make check
make run
```

Open http://127.0.0.1:8000. Python 3.12+ and uv are required. No API key, external assets or AI calls are used.

## Review the demo

1. Open Lena Voss, Maison Aurelle or Juno Park.
2. Review the twelve sections using the section navigation. Source chips show their fictional brief on hover or focus and link to the source entry.
3. Change scoring weights. Ranking updates locally; weights normalize to 100. The prepared demo does not automatically change.
4. Open Sample context to compare a prewritten, more specific plan with the base fixture. This is a bundle preview, not free-form refinement.
5. Copy a section or message, export Markdown or JSON with current weights, or print the plan or day brief. Import exported JSON from the partner selection page to restore it.
6. Clear session to remove the current studio. Sessions expire after 30 idle minutes; exported files remain on your device.

The three fixtures deliberately differ. Lena's plan protects authorship and client NDAs. Maison Aurelle's plan makes approval ownership explicit. Juno's plan starts with listening and permission, with several uses excluded.

## Current boundaries

Scores, time estimates and thresholds are planning judgments against fictional evidence. Verify before real outreach. There is no live research, generation, editable content, arbitrary context-layer recomputation, access-code gate or public deployment. Inline edits, verification, locks and comparison remain M3 work. The print stylesheet targets a one-page A4 day brief; printer-specific pagination requires review.

The app uses FastAPI, Pydantic v2 and Jinja2 with local CSS and a small native JavaScript controller. No JavaScript build step or third-party runtime requests. Browser storage holds only a theme preference; JSON export/import provides explicit persistence. Run a single server process: sessions are process-local and disappear on restart.

Quality checks cover strict types, lint, formatting, all six fixture schemas, twelve-section rendering, evidence integrity, capabilities, tailoring, ranking, session isolation/expiry, hostile HTML escaping and import/export round trips. The browser audit and remaining limits are in [M1 verification](evals/reports/M1.md).

[Milestone plan](docs/PLAN.md) · [Decisions](docs/DECISIONS.md) · [Architecture](docs/ARCHITECTURE.md) · [Privacy](docs/PRIVACY.md) · [Run and deployment](docs/DEPLOY.md)

MIT licensed. Fictional data implies no affiliation or endorsement.
