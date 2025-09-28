from langchain_core.tools import tool
from . import db


@tool("add_user", return_direct=True)
def add_user_tool(user_id: int | None = None, name: str | None = None) -> str:
    """Add a new user by (user_id, name)."""
    if user_id is None or not name:
        return "Please provide both user_id and name, e.g., `add user 1 Alice`."
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return "user_id must be an integer."
    return db.add_user(user_id, name.strip())

@tool("create_ticket", return_direct=True)
def create_ticket_tool(title: str, assignee_name: str) -> str:
    """Create a new ticket with a title and assign to existing user by name."""
    return db.create_ticket(title, assignee_name)

@tool("view_ticket", return_direct=True)
def view_ticket_tool(user_id: int) -> str:
    """View a ticket title by user_id, or not-found message."""
    return db.view_ticket_title(user_id)

@tool("update_status", return_direct=True)
def update_status_tool(user_id: int, status: str) -> str:
    """Update ticket status to OPEN | IN_PROGRESS | CLOSED."""
    return db.update_ticket_status(user_id, status)

@tool("list_tickets", return_direct=True)
def list_tickets_tool(kind: str = "all") -> str:
    """List tickets as a table. kind = all | OPEN | IN_PROGRESS | CLOSED."""
    return db.list_tickets(kind)

@tool("reset_database", return_direct=True)
def reset_database_tool() -> str:
    """Reset the database by deleting all users and tickets."""
    return db.reset_db()

@tool("delete_user", return_direct=True)
def delete_user_tool(user_id: int) -> str:
    """Delete a user (and their tickets) by user_id."""
    return db.delete_user(user_id)

@tool("delete_ticket", return_direct=True)
def delete_ticket_tool(user_id: int) -> str:
    """Delete a ticket by user_id."""
    return db.delete_ticket(user_id)

@tool("show_users", return_direct=True)
def show_users_tool() -> str:
    """Show all users currently in the system."""
    users = db.show_users()
    return "No users found." if not users else "Users:\n" + "\n".join(f"{u['user_id']}: {u['name']}" for u in users)