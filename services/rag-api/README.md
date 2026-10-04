# rag-api

Question answering over company documents. Retrieves documents with PostgreSQL + pgvector
and local embeddings, filters them by the caller's group, and generates the answer
through the model gateway.

## Files

| File | What it does |
|---|---|
| `app.py` | API: `/ask` answers a question from the documents the caller may read |
| `ingest.py` | Creates the `docs` table and stores documents with their embeddings |
| `search.py` | Finds the 3 documents closest in meaning to a question |

## Requirements

- Gateway and database running: `docker compose up -d` in the repo root
  (PostgreSQL with pgvector on `localhost:5433`, database `platform`, user/password `llm`)
- `TEAM_KEY` in `.env`: a gateway key with access to the `fast` model
- Embedding model `BAAI/bge-small-en-v1.5` (384 dimensions), runs locally, downloaded on first run

## Run

```bash
uv run python ingest.py
uv run python search.py "how many vacation days do I have?"
uv run --env-file ../../.env uvicorn app:app --port 8001
```

## API

### `GET /healthz`

Returns `{"ok": true}`.

### `POST /ask`

| Part | Value |
|---|---|
| Header `X-User-Group` | Caller's group, e.g. `staff` or `finance`. Required. |
| Body | `{"question": "..."}`, max 2000 characters |
| Response | `{"answer": "...", "sources": ["hr-001", ...]}` |

```bash
curl -s localhost:8001/ask -H "Content-Type: application/json" -H "X-User-Group: staff" \
  -d '{"question":"How much paid holiday do I get?"}' | jq
```

| Status | Meaning |
|---|---|
| 200 | Answer returned |
| 401 | `X-User-Group` header missing |
| 413 | Question longer than 2000 characters |

The model is told to answer only from the retrieved documents, to say it does not know
otherwise, to cite document IDs like `[hr-001]`, and not to reveal its instructions.
Calls use the `fast` model with temperature 0.

## Access control

Every caller may read `staff` documents. Documents of other groups are only searched
when the caller belongs to that group. Filtering happens in the database query,
before any text is sent to the model.

| Caller group | Documents searched |
|---|---|
| `staff` | `staff` |
| `finance` | `staff`, `finance` |

## API test results

Question: "When are quarterly budget reviews?"

| Caller group | Sources returned | Answer |
|---|---|---|
| `staff` | hr-001, it-001, hr-002 | "I don't know." |
| `finance` | fin-001, hr-001, it-001 | "Quarterly budget reviews happen in the first week of each quarter [fin-001]." |

`fin-001` is not retrieved for `staff`, so it is never sent to the model.

## Tracing

`ask`, `retrieve` and `generate` are traced in Langfuse with the `@observe()` decorator.
The model call also appears in the gateway trace.

## Table `docs`

| Column | Type | Content |
|---|---|---|
| `id` | text | Document ID, e.g. `hr-001` |
| `acl_group` | text | Group allowed to read it: `staff` or `finance` |
| `content` | text | Document text |
| `embedding` | vector(384) | Embedding of the text |

## Settings

| Variable | Default |
|---|---|
| `PLATFORM_DSN` | `postgresql://llm:llm@localhost:5433/platform` |
| `GATEWAY_URL` | `http://localhost:4000` |
| `TEAM_KEY` | none, required |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` | from `.env` |

## Search

- Distance is cosine distance (`<=>`). Lower means closer in meaning.
- `search.py` does not filter by `acl_group`. `app.py` does.
- Running `ingest.py` again updates existing IDs and does not create duplicates.

## Search test

```bash
for q in \
  "can I work from home?" \
  "who do I tell if my laptop is hacked?" \
  "when is the budget meeting?" \
  "what is the capital of France?" \
  "Kolik mám dní dovolené?" \
  "hr-001"
do
  echo "== $q"
  uv run python search.py "$q"
  echo
done
```

Results:

```
== can I work from home?
0.350 [hr-002] Remote work is allowed. Office attendance is optional.
0.476 [hr-001] Employees get 5 weeks of paid holiday per year.
0.534 [it-001] Report security incidents to the on-call engineer within 1 hour.

== who do I tell if my laptop is hacked?
0.424 [it-001] Report security incidents to the on-call engineer within 1 hour.
0.591 [hr-002] Remote work is allowed. Office attendance is optional.
0.649 [fin-001] Quarterly budget reviews happen in the first week of each quarter.

== when is the budget meeting?
0.383 [fin-001] Quarterly budget reviews happen in the first week of each quarter.
0.534 [it-001] Report security incidents to the on-call engineer within 1 hour.
0.541 [hr-001] Employees get 5 weeks of paid holiday per year.

== what is the capital of France?
0.659 [hr-001] Employees get 5 weeks of paid holiday per year.
0.671 [fin-001] Quarterly budget reviews happen in the first week of each quarter.
0.686 [hr-002] Remote work is allowed. Office attendance is optional.

== Kolik mám dní dovolené?
0.517 [hr-001] Employees get 5 weeks of paid holiday per year.
0.523 [hr-002] Remote work is allowed. Office attendance is optional.
0.523 [it-001] Report security incidents to the on-call engineer within 1 hour.

== hr-001
0.457 [it-001] Report security incidents to the on-call engineer within 1 hour.
0.482 [hr-002] Remote work is allowed. Office attendance is optional.
0.524 [hr-001] Employees get 5 weeks of paid holiday per year.
```

- Paraphrased English questions: correct, distance below 0.43.
- Unrelated question: all results above 0.65.
- Czech question: no clear match. 
- Document IDs: not matched. Needs keyword search.