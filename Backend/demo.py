#!/usr/bin/env python3
import os, sys, time
from mini_jira_admin_agent.graph import build_app
from utils.compact_history import compact_history

def main():
    print("Mini-Jira Admin Agent — type 'exit' to quit.\n")
    app = build_app()
    history = []  # list of {"role": "user"/"assistant", "content": str}
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        history = compact_history(history, max_window=12, max_chars=6000)
        # Run one turn
        result = app.invoke({"messages": history + [{"role": "user", "content": user}]})
        msg = result["messages"][-1]["content"]
        print(f"Bot: {msg}\n")
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": msg})

if __name__ == "__main__":
    main()
