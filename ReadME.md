# 📝 Mini-Jira Admin Agent (LangGraph + FastAPI + React)

A **full-stack Jira-like agent** that manages tickets and users via **natural language**.

* **Frontend**: React + Vite (UI for user interaction)
* **Backend**: FastAPI (API for database + LLM routing)
* **Database**: SQLite (auto-created if not present)
* **AI Layer**: LangGraph + local Ollama model (`llama3`) for natural-language intent parsing and routing

---

## 🚀 Features

* **User Management**

  * Add new users
  * Delete users by `user_id`

* **Ticket Management**

  * Create tickets and assign to users

    * Prevents duplicate titles
    * Validates user existence
  * View ticket by ID (with not-found handling)
  * Update ticket status (`OPEN | IN_PROGRESS | CLOSED`) using natural language
  * Delete tickets by `user_id`

* **Listing & Status**

  * List all tickets in a clean **table view**
  * Filter tickets by status (`open`, `closed`, `in-progress`, or all)

* **Database Operations**

  * Reset database (clear all users & tickets)
  * Auto-create `database.db` if missing

* **Conversation Handling**

  * Prompts for missing information (e.g., assignee for new tickets)
  * History compaction to prevent memory overload

---

## 🛠 Project Structure

```
Mini-Jira_Admin_Agent/
├─ Backend/                        # FastAPI backend
│  ├─ __pycache__/                 # Python cache files
│  ├─ mini_jira_admin_agent/       # Core backend package
│  │   ├─ config.py                # Backend/model config
│  │   ├─ db.py                    # SQLite helpers
│  │   ├─ tools.py                 # DB operations (add user, create ticket, etc.)
│  │   ├─ graph.py                 # LangGraph router + tool nodes
│  │   ├─ nlp_prompts.py           # System prompt for routing
│  │   └─ __init__.py
│  │
│  ├─ tests/                       # Backend tests
│  │   └─ test_sample.py
│  │
│  ├─ utils/                       # Utility helpers
│  │   ├─ database_creation.py     # Explicit DB creation helper
│  │   └─ compact_history.py       # History compaction logic
│  │
│  ├─ .DS_Store                    # macOS metadata (safe to gitignore)
│  ├─ ReadME.md                    # Backend-specific README
│  ├─ database.db                  # SQLite database (auto-created; consider gitignore)
│  ├─ demo.py                      # CLI chatbot loop (optional)
│  ├─ requirements.txt             # Python dependencies
│  └─ server.py                    # FastAPI entrypoint
│
├─ Frontend/                       # React + Vite frontend
│  ├─ public/                      # Static assets
│  ├─ src/                         # React source files
│  │   ├─ components/              # Reusable UI components
│  │   ├─ pages/                   # Page-level views
│  │   ├─ App.jsx                  # Root React component
│  │   └─ main.jsx                 # Entry point for ReactDOM
│  │
│  ├─ .gitignore
│  ├─ README.md                    # Frontend-specific README
│  ├─ components.json              # Config for UI components (shadcn/ui if used)
│  ├─ eslint.config.js             # ESLint config
│  ├─ index.html                   # Base HTML template
│  ├─ jsconfig.json                # JS path aliases
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ postcss.config.js            # PostCSS config
│  ├─ tailwind.config.js           # Tailwind CSS config
│  └─ vite.config.js               # Vite config
│
└─ ReadME.md                       # Root README (main project overview)
```

---

## ⚡ Example Queries (via UI or CLI)

```bash
# add user
add user 1 Alice

# create ticket
create ticket Login for Alice

# view ticket for user 1
view ticket for user id 1

# change ticket status
update ticket status to closed for Alice

# list tickets
list tickets
list tickets with status open

# delete ticket
delete ticket for Alice

# reset database
reset database
```

---

## 🖥️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Dhruvil03/Mini-Jira_Admin_Agent.git
cd Mini-Jira_Admin_Agent
```

### 2. Start Ollama (for LLM routing)

```bash
ollama pull llama3
ollama serve
```

### 3. Backend Setup (FastAPI)

```bash
cd backend
python -m venv jira_env

# MacOS/Linux
source jira_env/bin/activate

# Windows (PowerShell)
.\jira_env\Scripts\Activate.ps1

pip install -r requirements.txt

# Run backend server
uvicorn server:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

### 4. Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend will start on `http://localhost:5173`
Backend runs on `http://127.0.0.1:8000`

---

## 🧠 Design

* **LangGraph Router** for natural-language intent recognition
* **FastAPI Backend** for DB operations and API routes
* **React + Vite Frontend** for a modern, responsive UI
* **SQLite Database** for persistent storage
* **History Compaction** keeps conversations efficient 

---

# Flowchart
<img width="1393" height="381" alt="Data Preprocessing Pipeline" src="https://github.com/user-attachments/assets/b84af8aa-6d05-427f-aec8-c5e4367456cd" />

---

## 🙌 Contributions

Feel free to **fork**, **open an issue**, or **submit a PR** to improve the project!

👉 [Mini-Jira Admin Agent Repository](https://github.com/Dhruvil03/Mini-Jira_Admin_Agent)

---
