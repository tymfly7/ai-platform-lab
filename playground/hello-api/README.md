# hello-api

A minimal FastAPI service, containerized with Docker and uv.
It's the first building block of the AI Platform Lab: the same pattern
(FastAPI + uv + a small container image) is reused for the RAG API and agent services later.

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/` | Service name and link to the docs |
| GET | `/healthz` | `{"ok": true}`, used as a health check |
| GET | `/hello/{name}` | `{"message": "Hello <name>"}` |
| GET | `/docs` | Interactive API docs (Swagger UI) |

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn main:app --reload --port 8200
curl -s localhost:8200/healthz
```

## Run in Docker

```bash
docker build -t hello-api .
docker run -d --rm --name hello-api -p 8200:8200 hello-api
curl -s localhost:8200/healthz
docker stop hello-api
```

## How the image is built

- Base image `python:3.14-slim`, matching `.python-version`
- `UV_PYTHON_DOWNLOADS=never`: the build fails clearly if the Python version doesn't match,
  instead of silently downloading another interpreter
- Dependencies are installed from `uv.lock` **before** the code is copied, so code changes
  don't trigger a full dependency reinstall (layer caching)
- `.dockerignore` keeps the local `.venv` out of the image

## What I learned

- Port mapping is `-p HOST:CONTAINER`; the container port must match uvicorn's `--port`
- `docker build .` only sees the current folder, so `main.py`, `pyproject.toml`, `uv.lock`
  and the `Dockerfile` must sit side by side
- A FastAPI `{"detail":"Not Found"}` means the server is running but the route doesn't exist