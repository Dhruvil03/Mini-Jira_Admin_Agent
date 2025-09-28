# Mini-Jira Admin Agent (LangGraph)

A terminal-based chatbot that manages a tiny Jira-like SQLite database via natural-language using **LangGraph**.
It supports:
- Add new user
- Create new ticket & assign to user (with duplicate-title and user-existence checks)
- View ticket title by id (handles not-found)
- Responds with `I can’t help with ...` for unsupported actions

## Bonus Capabilities (included)
- Asks back when information is missing (e.g., missing assignee for a new ticket)
- Adds a `status` column with `OPEN | IN_PROGRESS | CLOSED`
- Natural-language status updates (`change status to closed for user_id <user_id>`, etc.)
- List tickets (open/closed/in-progress/all) as a table
- PyTest test
- History compaction to avoid exploding memory
- ReadME added

## Additional Capabilities (included)
- Delete user (using user_id)
- Delete ticket (using user_id)
- Reset Database (clear all the entries in both users and ticket tables)
- If database is not in the folder than it will create a new database (i.e. - database.db) by itself.

## Requirements
- Local Ollama model (`llama3`) — install Ollama and run it.

# How to setup the project
Run Ollama (run in different terminal):
```bash
ollama serve
```

Install dependencies:
```bash
python -m venv jira_env
source jira_env/bin/activate
pip install -r requirements.txt
```

Run the terminal chat:
```bash
python demo.py
pytest -q 
```

# Example Queries
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

# list tickets with status = OPEN (#List tickets with particular status)
list tickets with status open 

# delete ticket
delete ticket for Alice

# reset database
Reset database

exit
```

## Project Structure
```
mini_jira_admin_agent/
├─ demo.py                   # Terminal chat loop
├─ requirements.txt
├─ mini_jira_admin_agent/
│  ├─ config.py              # Backend/model selection
│  ├─ db.py                  # SQLite helpers 
│  ├─ tools.py               # DB tools (add user, create ticket, etc.)
│  ├─ graph.py               # LangGraph: router + tool nodes
│  ├─ nlp_prompts.py         # Router system prompt
└─ tests/
│   └─ test_sample.py
└─ utils/
    └─ database_creation.py  # python code to create database (explicitly)
    └─ compact_history.py    # history compaction to avoid exploding memory
```

## Design
- **LangGraph** graph with nodes:
  - `route` (LLM) → emits `intent` + extracted arguments
  - tool nodes: `add_user`, `create_ticket`, `view_ticket`, `update_status`, `list_tickets`
  - `unsupported` for unsupported intents, `clarify` when info is missing
- **Exploding history** is mitigated by a small rolling window + periodic summary compaction.
- We keep natural-language routing via the LLM to meet the requirement “use LLMs for natural-language conversations.”
- The DB logic is separated in `tools.py`.
- Ticket creation validates user existence and duplicate titles.

## AI Usage Disclosure
Parts of this project (ReadME, test case, code checking) were created with the assistance of an AI (gpt-oss-120B, ChatGPT). Logic was reviewed and adapted for clarity and correctness.

# 🙌 Contributions / Issues
Feel free to fork, raise an issue, or create a pull request if you'd like to contribute or report bugs.

GitHub Repository:  https://github.com/Dhruvil03/SAP_Assessment