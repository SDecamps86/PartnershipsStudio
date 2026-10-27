FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
WORKDIR /srv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
COPY atelier ./atelier
COPY fixtures ./fixtures
COPY config ./config
COPY site ./site
COPY scripts ./scripts
RUN PYTHONPATH=/srv .venv/bin/python scripts/build_demo.py
RUN useradd --uid 10001 --create-home studio
USER studio
EXPOSE 8000
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
