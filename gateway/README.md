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

## Apply config changes

```bash
docker compose up -d --force-recreate litellm
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

## Test results (team-news key)

| Test | Result |
|---|---|
| Call `fast` | 200, answer returned |
| Call `smart` | Refused: model not allowed for this key |
| 7 calls in one minute | 4 × 200, then 429 |
| Spend after tests | $0.00017625 |