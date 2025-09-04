import sqlite3, argparse

# establishing connection
def get_conn():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row    # it will return object instead of tuple
    conn.execute("PRAGMA foreign_keys = ON;") # explicitly giving foreign key constraint
    return conn

# if database does not exists
def init_db():
    conn = sqlite3.connect("./database.db") # file path
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        assignee_id INTEGER NOT NULL UNIQUE,
        status TEXT CHECK(status IN ('OPEN', 'IN_PROGRESS', 'CLOSED')) DEFAULT 'OPEN',
        FOREIGN KEY (assignee_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database and tables created successfully.")
    
def add_user(user_id: int, name: str) -> str:
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO users (id, name) VALUES (?, ?)",
                (user_id, name)
            )
            conn.commit()
            return "The user is added."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.name" in str(e):
                return "Username already exists."
            elif "UNIQUE constraint failed: users.id" in str(e):
                return "User ID already exists."
            raise

def delete_user(user_id: int) -> str:
    with get_conn() as conn:
        try:
            conn.execute("DELETE FROM tickets WHERE assignee_id = ?", (user_id,))
            cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cur.rowcount == 0:
                return f"User with id {user_id} does not exist."
            conn.commit()
            return f"User with id {user_id} (and their tickets) deleted successfully."
        except Exception as e:
            return f"Error while deleting user {user_id}: {e}"

def create_ticket(title: str, assignee_name: str) -> str:
    with get_conn() as conn:
        # user must exist
        row = conn.execute("SELECT id FROM users WHERE name = ?", (assignee_name,)).fetchone()
        if not row:
            return f"Cannot create ticket: user '{assignee_name}' does not exist."
        assignee_id = row["id"]
        # prevent duplicates by title
        dup = conn.execute("SELECT id FROM tickets WHERE title = ?", (title,)).fetchone()
        if dup:
            return "Cannot create ticket: duplicate title."
        cur = conn.execute(
            "INSERT INTO tickets(title, assignee_id, status) VALUES (?, ?, 'OPEN')",
            (title, assignee_id),
        )
        ticket_id = cur.lastrowid    # column "id" is INTEGER PRIMARY KEY
        conn.commit()
        return f"Ticket created with id {ticket_id}."

def view_ticket_title(user_id: int) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT title FROM tickets WHERE assignee_id = ?", (user_id,)).fetchone()
        if not row:
            return f"Ticket with user id {user_id} does not exist."
        return row["title"]

def update_ticket_status(user_id: int, status: str) -> str:
    status = status.upper()
    if status not in {"OPEN", "IN_PROGRESS", "CLOSED"}:
        return "Invalid status. Use OPEN, IN_PROGRESS, or CLOSED."
    with get_conn() as conn:
        cur = conn.execute("UPDATE tickets SET status = ? WHERE assignee_id = ?", (status, user_id))
        if cur.rowcount == 0:
            return f"Ticket with id {user_id} does not exist."
        conn.commit()
        return f"Ticket with id {user_id} status updated to {status}."

def delete_ticket(user_id: int) -> str:
    with get_conn() as conn:
        try:
            cur = conn.execute("DELETE FROM tickets WHERE assignee_id = ?", (user_id,))
            if cur.rowcount == 0:
                return f"Ticket with user_id {user_id} does not exist."
            conn.commit()
            return f"Ticket with user_id {user_id} deleted successfully."
        except Exception as e:
            return f"Error while deleting ticket for user id {user_id}: {e}"

def list_tickets(kind: str = "all") -> str:
    kind = kind.lower().replace("-", "_")
    query = "SELECT t.id, t.title, t.assignee_id, u.name AS assignee, t.status FROM tickets t JOIN users u ON t.assignee_id = u.id"
    params = ()
    if kind in {"open", "in_progress", "closed"}:
        query += " WHERE t.status = ?"
        params = (kind.upper(),)
    query += " ORDER BY t.id ASC"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    if not rows:
        return "No tickets found."
    # table format
    from tabulate import tabulate
    headers = ["id", "title", "assignee", "status"]
    table = tabulate([[r["id"], r["title"], r["assignee_id"], r["assignee"], r["status"]] for r in rows], headers=["id","title","assignee_id","assignee","status"], tablefmt="github")
    return table

def reset_db() -> str:
    """Delete all rows from tickets and users tables (reset the database)."""
    with get_conn() as conn:
        try:
            conn.execute("DELETE FROM tickets;")
            conn.execute("DELETE FROM users;")
            conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('tickets','users');")
            conn.commit()
            return "Database reset: all users and tickets deleted."
        except Exception as e:
            return f"Error while resetting database: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Initialize database")
    args = parser.parse_args()
    if args.init:
        init_db()
else:
    # Auto-init on import if database not exists
    with get_conn() as conn:
        row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';").fetchone()
        if not row:
            init_db()
        
