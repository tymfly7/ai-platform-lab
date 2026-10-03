# gateway

LiteLLM proxy configuration. The container is defined in the root `docker-compose.yml`, which mounts `config.yaml` into it.

## Models

| Name | Provider model | Setting |
|---|---|---|
| `fast` | gemini/gemini-3.8-flash | reasoning_effort: low |
| `smart` | gemini/gemini-3.8-flash | reasoning_effort: high |

- Fallback: `smart` → `fast`
- Retries: 2

## Settings

| Setting | Source |
|---|---|
| Master key | `LITELLM_MASTER_KEY` in `.env` |
| Database | `DATABASE_URL` in `docker-compose.yml` |
| Gemini key | `GEMINI_API_KEY` in `.env` |
| Langfuse keys | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` in `.env` |
| Langfuse address | `LANGFUSE_OTEL_HOST` in `docker-compose.yml` |

## Run

From the repo root:

```bash
docker compose up -d                                   # start gateway and database
curl -s localhost:4000/health/liveliness               # check it is up
docker compose logs -f litellm                         # follow logs
docker compose up -d --force-recreate litellm          # apply changes to config.yaml
docker compose down                                    # stop
```

Test call with a team key:

```bash
curl -s localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer <team key>" -H "Content-Type: application/json" \
  -d '{"model":"fast","messages":[{"role":"user","content":"Say hello"}]}' \
  | jq '.choices[0].message.content'
```

## Create a team key

```bash
set -a; source .env; set +a
curl -s localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" -H "Content-Type: application/json" \
  -d '{"key_alias":"team-news","models":["fast"],"max_budget":1,"rpm_limit":5,"metadata":{"team":"news"}}' \
  | jq -r .key
```

| Field | Meaning |
|---|---|
| `models` | Models the key may use |
| `max_budget` | Spend limit in USD |
| `rpm_limit` | Requests per minute |

## Check spend

```bash
curl -s "localhost:4000/key/info?key=<team key>" -H "Authorization: Bearer $LITELLM_MASTER_KEY" | jq .info.spend
```

Admin UI: http://localhost:4000/ui (log in with the master key)

## Tracing

Calls are sent to Langfuse with the `langfuse_otel` callback.

Traces: http://localhost:3000, under Tracing. Each call creates a `litellm_request` entry
(input, output, model, tokens, cost, key alias) and a `raw_gen_ai_request` entry.

Check for tracing errors:

```bash
docker compose logs litellm --since 5m | grep -i -E 'langfuse|otel'
```

## Test results (team-news key)

| Test | Result |
|---|---|
| Call `fast` | 200, answer returned |
| Call `smart` | Refused: model not allowed for this key |
| 7 calls in one minute | 4 × 200, then 429 |
| Spend after tests | $0.00017625 |
| Trace in Langfuse | Call recorded with model, tokens, cost and key alias |