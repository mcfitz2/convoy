FROM python:slim AS backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY ./ ./

RUN uv sync
ENV VIRTUAL_ENV=/app/.venv
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "run", "main/main.py", "--port", "80"]

EXPOSE 80
