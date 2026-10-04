# Security model
![alt text](image.png)
Risks from the OWASP Top 10 for LLM Applications, the control for each in this repo,
and its current state.

| Risk | Control | Where | State |
|---|---|---|---|
| Prompt injection | System prompt limits answers to retrieved documents; write tools need human approval | `services/rag-api/app.py`, `services/agent/agent.py`, `evals/` | Implemented, tested automatically (one check, see limitations in `evals/README.md`) |
| Sensitive information disclosure | Documents filtered by caller group in the database query, before the prompt is built | `services/rag-api/app.py` (`retrieve`), `evals/` | Implemented, tested automatically on every pull request |
| Excessive agency | Tool allowlist, approval for write tools, step limit of 6, audit log | `services/agent/agent.py` | Implemented, tested manually |
| Unbounded consumption | Per-key budget and requests-per-minute limit in the gateway | `gateway/`, team keys | Implemented, tested (429 after limit) |
| Secrets exposure | Vendor key only in the gateway; apps use virtual keys; `.env` not in git | `gateway/`, `.gitignore` | Implemented |
| Supply chain | Dependencies pinned in `uv.lock`; container images by tag | `uv.lock` files, `docker-compose.yml` | Partly: images not pinned by digest |

## Known gaps

- Caller identity comes from the `X-User-Group` header. Any caller can set it.
- The approval endpoint has no authentication. Any caller can approve under any name.
- Automated tests cover the RAG API only. The agent has no automated tests.

## Data handling

- Leaves the machine: questions, retrieved document text and answers are sent to
  Google Gemini through the gateway.
- Stored: prompts, answers, token counts and cost are stored in Langfuse (local).
  Keys and spend are stored in the gateway database (local).
- Retention: no retention limit is configured.
- Personal data: not filtered. Test documents contain no personal data.