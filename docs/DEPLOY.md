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
