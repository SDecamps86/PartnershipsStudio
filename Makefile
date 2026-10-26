.PHONY: run check eval
run:
	uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
	uv run pytest tests
	uv run python -m evals.run
eval:
	uv run python -m evals.run
