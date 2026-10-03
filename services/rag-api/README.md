# rag-api

Document retrieval with PostgreSQL + pgvector and local embeddings.

## Files

| File | What it does |
|---|---|
| `ingest.py` | Creates the `docs` table and stores documents with their embeddings |
| `search.py` | Finds the 3 documents closest in meaning to a question |

## Requirements

- PostgreSQL with pgvector on `localhost:5433` (database `platform`, user/password `llm`)
- Embedding model `BAAI/bge-small-en-v1.5` (384 dimensions), runs locally, downloaded on first run

Start the database:

```bash
docker run -d --name pg -e POSTGRES_USER=llm -e POSTGRES_PASSWORD=llm \
  -e POSTGRES_DB=platform -p 5433:5432 pgvector/pgvector:pg16
```

## Run

```bash
uv run python ingest.py
uv run python search.py "how many vacation days do I have?"
```

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

## Search

- Distance is cosine distance (`<=>`). Lower means closer in meaning.
- Results are not filtered by `acl_group`.
- Running `ingest.py` again updates existing IDs and does not create duplicates.

## Test example
```
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

===RESULTS===`
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

