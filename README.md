# AI Platform Lab

A learning project in AI platform engineering.

An AI platform is the shared layer a company puts between its teams and AI models.
Teams build AI features on top of it. The platform controls who may use which model,
how much they may spend, which documents an AI may read, and how answers are tested
and monitored.

This repo contains a small version of such a platform. It runs locally with Docker.
Models: Google Gemini (paid API) and Ollama (local).

## The Journey

| Component | What it does | Folder | State |
|---|---|---|---|
| Model gateway | One entry point for all model calls. Each team gets its own key with allowed models, a request limit per minute and a spending limit. Tracks cost per key. | `gateway/` | Working |
| Document search | Stores company documents with embeddings in PostgreSQL (pgvector) and finds the ones closest in meaning to a question. | `services/rag-api/` | Working |
| Model experiments | Scripts that call models directly, measure token usage, and test how much answers vary between runs. | `playground/llm-basics/` | Working |
| Containerized API | A minimal FastAPI service packaged as a Docker image. Template for the other services. | `playground/hello-api/` | Working |
| Tracing | Records every model call, search and tool use, with timing and cost. | | Working |
| Question answering with access control | Answers questions from documents. Each user only gets answers from documents their group may read. | | Working |
| Agent with human approval | An AI that uses tools. Actions that change something wait for a person to approve them. | | Working |
| Automated evaluation | Tests answer quality and safety on every code change in GitHub Actions. | | Planned |
| Cloud deployment | Runs the gateway in Azure, with secrets in Key Vault and deployment from GitHub without stored passwords. | | Planned |

## Setup

Requirements: Docker, [uv](https://docs.astral.sh/uv/), a Gemini API key.

```bash
git clone https://github.com/<your-user>/ai-platform-lab.git
cd ai-platform-lab
cp .env.example .env          # then set GEMINI_API_KEY in .env
docker compose up -d
```

## Local stack

`docker-compose.yml` starts the shared services. Settings come from `.env`.

| Service | Image | Port | Used for |
|---|---|---|---|
| litellm | ghcr.io/berriai/litellm:main-stable | 4000 | Model gateway |
| db | pgvector/pgvector:pg16 | 5433 | Gateway keys and spend, document embeddings |

```bash
docker compose up -d          # start
docker compose ps             # status
docker compose logs litellm   # gateway logs
docker compose down           # stop (data is kept in the pgdata volume)
```

## Folders

| Folder | Content |
|---|---|
| `gateway/` | Gateway configuration |
| `services/rag-api/` | Document ingest and search |
| `playground/hello-api/` | Minimal FastAPI service with Dockerfile |
| `playground/llm-basics/` | Model call and nondeterminism scripts |
| `docs/` | Architecture notes, decision records, incident reports |

## License

MIT