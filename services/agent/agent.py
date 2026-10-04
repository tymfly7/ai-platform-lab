import json
import os
import uuid

from fastapi import FastAPI, HTTPException
from langfuse import observe
from openai import OpenAI
from pydantic import BaseModel

llm = OpenAI(base_url=os.environ.get("GATEWAY_URL", "http://localhost:4000"),
             api_key=os.environ["TEAM_KEY"])
app = FastAPI(title="agent")
MAX_STEPS = 6


def get_ticket(ticket_id: str) -> dict:
    return {"id": ticket_id, "status": "open", "title": "VPN not working"}


def close_ticket(ticket_id: str, reason: str) -> dict:
    return {"id": ticket_id, "status": "closed", "reason": reason}


TOOLS = {
    "get_ticket": {
        "fn": get_ticket, "needs_approval": False, "description": "Read a support ticket",
        "parameters": {"type": "object", "properties": {"ticket_id": {"type": "string"}},
                       "required": ["ticket_id"]},
    },
    "close_ticket": {
        "fn": close_ticket, "needs_approval": True, "description": "Close a support ticket",
        "parameters": {"type": "object",
                       "properties": {"ticket_id": {"type": "string"}, "reason": {"type": "string"}},
                       "required": ["ticket_id", "reason"]},
    },
}
TOOL_SPECS = [
    {"type": "function",
     "function": {"name": n, "description": t["description"], "parameters": t["parameters"]}}
    for n, t in TOOLS.items()
]
PENDING: dict[str, dict] = {}  # approval_id -> saved conversation (use a DB in production)


def audit(event: str, **fields):
    print(json.dumps({"audit": event, **fields}), flush=True)


@observe()
def run(messages: list) -> dict:
    for _ in range(MAX_STEPS):
        r = llm.chat.completions.create(model="fast", messages=messages, tools=TOOL_SPECS)
        msg = r.choices[0].message
        if not msg.tool_calls:
            return {"status": "done", "answer": msg.content}
        messages.append(msg.model_dump(exclude_none=True))
        waiting = []
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            tool = TOOLS.get(name)
            if tool and tool["needs_approval"]:
                waiting.append({"id": call.id, "name": name, "args": args})
                continue
            result = tool["fn"](**args) if tool else {"error": f"unknown tool {name}"}
            audit("tool_call", tool=name, args=args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
        if waiting:
            approval_id = str(uuid.uuid4())
            PENDING[approval_id] = {"messages": messages, "calls": waiting}
            audit("approval_requested", id=approval_id, calls=waiting)
            return {"status": "awaiting_approval", "approval_id": approval_id, "calls": waiting}
    return {"status": "stopped", "reason": f"reached {MAX_STEPS} steps"}


class Task(BaseModel):
    goal: str


class Decision(BaseModel):
    approve: bool
    approver: str


@app.post("/tasks")
def create_task(task: Task):
    messages = [
        {"role": "system", "content": "You are an IT support agent. Use the tools to act on tickets."},
        {"role": "user", "content": task.goal},
    ]
    return run(messages)


@app.post("/approvals/{approval_id}")
def decide(approval_id: str, d: Decision):
    state = PENDING.pop(approval_id, None)
    if state is None:
        raise HTTPException(404, "unknown or already decided approval")
    messages = state["messages"]
    for c in state["calls"]:
        result = TOOLS[c["name"]]["fn"](**c["args"]) if d.approve else {"error": f"rejected by {d.approver}"}
        messages.append({"role": "tool", "tool_call_id": c["id"], "content": json.dumps(result)})
    audit("approval_decided", id=approval_id, approver=d.approver, approved=d.approve)
    return run(messages)