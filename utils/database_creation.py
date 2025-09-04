import sqlite3

conn = sqlite3.connect("/Users/dhruvilsinhajaysinhchauhan/Downloads/LangChain_Project/langchain/database.db") # file path
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
    assignee_id INTEGER,
    status TEXT CHECK(status IN ('OPEN', 'IN PROGRESS', 'CLOSED')) DEFAULT 'OPEN',
    FOREIGN KEY (assignee_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully.")
