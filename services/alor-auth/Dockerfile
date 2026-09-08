FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY packages/ ./packages/
COPY services/alor-auth/ ./services/alor-auth/

ENV PYTHONPATH=/app/packages:/app/services/alor-auth
ENV PATH=/app/.venv/bin:$PATH

CMD ["python", "services/alor-auth/main.py"]
