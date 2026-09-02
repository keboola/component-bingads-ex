FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code/

COPY pyproject.toml .
COPY uv.lock .

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --all-groups --frozen

COPY src/ src
COPY tests/ tests
# Not read at run time, but the test suite asserts on configSchema.json.
COPY component_config/ component_config
COPY scripts/ scripts
COPY .flake8 .
COPY deploy.sh .

CMD ["python", "-u", "src/component.py"]