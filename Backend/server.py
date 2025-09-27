# server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from mini_jira_admin_agent import tools, db
from mini_jira_admin_agent.graph import build_app as run_langgraph  # your LangGraph router

app = FastAPI(title="Mini-Jira Admin Agent API", version="1.0")

# Allow frontend (Vite dev server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Models --------
class ChatIn(BaseModel):
    message: str

class NewUser(BaseModel):
    user_id: int
    name: str

class NewTicket(BaseModel):
    title: str
    assignee: str

class StatusIn(BaseModel):
    status: Literal["OPEN", "IN_PROGRESS", "CLOSED"]

# =========================================================
# 1️⃣ Natural-Language Mode (goes through LangGraph router)
# =========================================================
@app.post("/api/chat")
def chat(inp: ChatIn):
    """
    Chat endpoint: send free-text commands like
    'create ticket Login for Alice' or 'add user 1 Alice'.
    LangGraph router will parse and execute using tools.py.
    """
    try:
        reply = run_langgraph(inp.message)  # should return a string reply
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")

# =========================================================
# 2️⃣ Direct Structured API (calls tools.py directly)
# =========================================================

# ---- Users ----
@app.get("/api/users")
def list_users():
    try:
        return {"users": db.show_users()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List users failed: {e}")

@app.post("/api/users")
def add_user(u: NewUser):
    """Add a new user directly by ID + Name."""
    try:
        tools.add_user(u.user_id, u.name)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Add user failed: {e}")

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user by ID."""
    try:
        tools.delete_user(user_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete user failed: {e}")

# ---- Tickets ----
@app.get("/api/tickets")
def list_tickets(status: str = "ALL"):
    """List tickets, optionally filtered by status."""
    try:
        return {"tickets": tools.list_tickets(status)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"List tickets failed: {e}")

@app.post("/api/tickets")
def create_ticket(t: NewTicket):
    """Create a new ticket directly for a given assignee."""
    try:
        tools.create_ticket(t.title, t.assignee)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Create ticket failed: {e}")

@app.patch("/api/tickets/{tid}")
def update_ticket_status(tid: int, s: StatusIn):
    """Update status of a ticket by ID."""
    try:
        tools.update_status(tid, s.status)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update status failed: {e}")

@app.delete("/api/tickets/{tid}")
def delete_ticket(tid: int):
    """Delete a ticket by ID."""
    try:
        tools.delete_ticket(tid)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete ticket failed: {e}")

# ---- Reset ----
@app.post("/api/reset")
def reset_db():
    """Clear all entries (users + tickets)."""
    try:
        tools.reset_db()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Reset failed: {e}")
