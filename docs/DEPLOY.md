# Run and deploy

## Local M0 review

Install Python 3.12 and uv, then from this directory:

```sh
uv sync --frozen
make check
make run
```

Open http://127.0.0.1:8000. No key is required. `make run` disables access logs. `uv run pre-commit install` installs optional local formatting hooks.

## Container

```sh
docker build -t partnerships-studio .
docker run --rm -p 8000:8000 partnerships-studio
```

Container execution requires Docker and is not verified by the scaffold's Python tests.

## Publication after review

The supplied repository already exists; do not run `gh repo create`. Inspect `git remote -v`, commit history and ignored secrets before an explicitly approved push. No Render or Pages deployment is included in M0. M4 will provide an exact blueprint and static-only Pages workflow. Never put a public link to a private live deployment in the showcase.

Planned private environment: OPENAI_API_KEY, OPENAI_MODEL, ACCESS_CODES, DAILY_BUDGET_USD, MONTHLY_BUDGET_USD, SECRET_KEY. These are placeholders in M0, not enforced controls. Verify current provider budget behavior during M2/M4; application spend enforcement must not rely on an assumed dashboard hard cap.

## M1 operational notes

The demo now needs `fixtures/` and `config/` in its runtime directory; the Dockerfile includes both. Use exactly one uvicorn process because sessions are in memory. No API key is required or read. Imports are capped at 512,000 bytes and retained only in the active session. The local host binding remains `127.0.0.1` by default.

`make eval` runs offline fixture quality gates and writes `evals/reports/latest.md`. `make check` includes that runner alongside lint, formatting, strict types and route/session/security tests. Browser accessibility QA is separate and described in the M1 verification report.

## Pipeline revision

The app now maintains a session-local partner portfolio. Use a single worker; no durable pipeline storage or CRM synchronization exists. JSON exports save only the selected partner. The dashboard uses America/Los_Angeles for its reference date and displays fictional event times as PT. Restarts and idle expiry clear all in-session operational edits.

## Editable static demo

Build with `PYTHONPATH=. uv run python scripts/build_demo.py --output site/dist`. The output contains only index.html, static JS/CSS, fictional fixture JSON, its schema, and the walkthrough media. Any static host can serve it; hash routing needs no server rewrite. Browser changes are not persisted remotely.

The registered Sites checkout is the sibling `PartnershipsStudioDemo` directory, whose `.openai/hosting.json` must be reused. Sites requires the exact source commit to be pushed before saving/deploying a version. Do not claim publication from an expected URL or local ZIP alone. Do not store source credentials in a file or shell argument.

Current blocker: the supported helper's stdin submission was rejected by automatic desktop approval review (`sandbox_approval` disabled). Additional network/repository permissions did not resolve this terminal-input restriction. Registration exists, but no version was pushed or deployed. Resume from the existing Site once the execution policy permits the helper input. No account key should be pasted into chat.
