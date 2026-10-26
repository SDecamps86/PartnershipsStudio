# Internal workflow revision: verification

## Delivered

- Three primary tabs: intake-only Prepare, Pipeline and focused Partner detail.
- Five fictional partners; ten base/sharpened fixtures, each with ten candidates and all twelve original content sections.
- Computed current-stage occupancy, preparation states, task readiness, pending actions and upcoming events.
- Search, stage/status/audience filters, list/board layouts, desktop directory table and mobile partner cards.
- Partner overview covering identity, maturity, importance, context, exact workflow, audience and next experience, plus preparation and activation indicators.
- Separate content pages instead of a stacked twelve-section document. Full-plan print remains an explicit separate route.
- Session-isolated task/metric updates, validated against planned totals, preserved across partner and sample-context switching. Export/import includes tracking and weights.

## Automated validation

- Ruff lint/format and strict mypy pass.
- 21 application/security/session/scoring/navigation tests and 5 offline fixture/dashboard evaluations pass (26 total).
- All 15 detail views render for every partner in both base and sharpened variants (150 route render checks inside the parameterized test).
- Tests verify imports/exports, all twelve original sections in the print view, unsafe HTML escaping, bad imports, evidence/capability references, session isolation/expiry, readiness/funnel consistency, weight persistence, count validation, and preservation across navigation.
- Native JavaScript syntax check passes.

## Browser validation

- Tested filtering the directory to Circuit Vale, name entry to its workspace, and Workflow navigation showing only the workflow page.
- Updated Oria House Hotels from Introduction/Qualifying to Education/Qualified, changed invitation status, and completed the privacy-sandbox task. Overview readiness changed from 20% to 40%; the task remained checked on its dedicated page. Test edits were cleared before final review screenshots.
- Axe-core 4.10.3 checked WCAG 2 A/AA, WCAG 2.1 AA and best-practice rules across 19 desktop page/dialog states: zero violations after correcting tab-number contrast and the standalone day-brief heading hierarchy. Supporting output is in `UX-a11y.json`.
- Dark-theme pipeline, overview and day brief also returned zero violations. Remaining manual-review entries concern non-text arrow glyphs/native controls, not reported contrast failures. This does not establish complete assistive-technology certification.
- Prepare, Pipeline, Overview and Use cases tested at 375, 768 and 1440 CSS pixels. No horizontal document overflow. Partner detail loads only the selected content. Temporary viewport overrides were reset after QA.
- No application console errors observed during navigation, filtering and tracking interaction.
- Review images: `docs/screenshots/UX-prepare.png`, `UX-pipeline.png`, `UX-partner.png`.

## Limits

The pipeline is session-local; no database, external CRM, calendar, sending, product telemetry or live AI is connected. Events/counts are explicitly fictional seed records or manual updates. Readiness measures task completion, not conversion likelihood. JSON saves the selected partner, not the entire portfolio. Restart/idle expiry clears the session. Printer-specific pagination and Docker execution remain unverified.
