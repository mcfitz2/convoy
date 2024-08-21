FROM node:latest as build

WORKDIR /app/ui

COPY ui/package*.json .
RUN npm install -g pnpm
RUN pnpm install

ADD ui ./

RUN pnpm ng build --configuration=production --base-href /ui/ --deploy-url /ui/

FROM python:slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY --from=build /app/ui/dist/ui static

COPY backend/pyproject.toml .

RUN uv sync
ENV VIRTUAL_ENV=/app/.venv
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

COPY backend/* ./
CMD ["fastapi", "run", "main.py", "--port", "80"]

EXPOSE 80