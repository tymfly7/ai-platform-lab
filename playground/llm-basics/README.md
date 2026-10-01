# llm-basics

Scripts for calling LLMs through the OpenAI-compatible API, with Gemini and local Ollama.

## Files

| File | What it does |
|---|---|
| `first_call.py` | One Gemini call; prints the answer and token usage |
| `nondeterminism.py` | Asks 4 questions at temperature 0 and 1.5, counts the answers |

## Run

```bash
# first call (Gemini)
uv run --env-file ../../.env python first_call.py

# nondeterminism (Ollama, default)
uv run python nondeterminism.py

# nondeterminism (Gemini, 16 calls)
set -a; source ../../.env; set +a
LLM_API_KEY=$GEMINI_API_KEY \
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ \
LLM_MODEL=gemini-3.8-flash LLM_PAUSE=13 LLM_RUNS=2 \
uv run python nondeterminism.py
```

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:11434/v1` | API endpoint |
| `LLM_API_KEY` | `ollama` | API key |
| `LLM_MODEL` | `gemma4:e4b` | Model name |
| `LLM_PAUSE` | `0` | Seconds between calls |
| `LLM_RUNS` | `5` | Calls per question per temperature |

## Results (Ollama, gemma4:e4b, 5 runs)

| Question | Temperature 0 | Temperature 1.5 |
|---|---|---|
| Second largest city in Czechia | Brno x5 | Brno x4, Ostrava x1 (wrong) |
| One Nordic capital | Oslo x5 | Oslo x3, Copenhagen x1, Stockholm x1 |
| Random number 1–10 | 7 x5 | 7 x2, 6, 9, 8 |
| Coffee shop name in Prague | 2 different names | 5 different names |

## Findings

- Temperature 1.5 produced a wrong fact (Ostrava).
- Temperature 0 still varied once (coffee shop).
- "Random" numbers are biased to 7.
- Gemini free tier: about 5 requests per minute and a small daily limit; a 429 means the limit was hit.