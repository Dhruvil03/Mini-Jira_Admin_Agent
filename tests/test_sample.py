import os
import re
import sys
import subprocess
from pathlib import Path

import pytest

ENTRYPOINT_NAME = "demo.py"
PKG_DIR_NAME = "mini_jira_admin_agent"


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / ENTRYPOINT_NAME).exists() and (p / PKG_DIR_NAME).is_dir():
            return p
    raise RuntimeError(
        f"Could not locate repo root containing {ENTRYPOINT_NAME} and {PKG_DIR_NAME}/ starting from {start}"
    )


def run_chat(commands, repo_root: Path, workdir: Path, timeout=12) -> str:
    python_exe = sys.executable
    entry = repo_root / ENTRYPOINT_NAME
    if not entry.exists():
        pytest.skip(f"Entry file {ENTRYPOINT_NAME} not found at {repo_root}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)

    proc = subprocess.Popen(
        [python_exe, str(entry)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(workdir),
        text=True,
        bufsize=1,
        env=env,
    )
    try:
        full_input = "\n".join(commands + ["exit"]) + "\n"
        out, _ = proc.communicate(full_input, timeout=timeout)
        return out
    except subprocess.TimeoutExpired:
        proc.kill()
        partial = proc.stdout.read() if proc.stdout else ""
        pytest.fail("Chat process timed out.\n--- OUTPUT SO FAR ---\n" + partial)


@pytest.fixture
def temp_workdir(tmp_path):
    return tmp_path


def assert_any_pattern(text, patterns, label):
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE | re.DOTALL):
            return True
    return False


def must_match_any(text, patterns, label):
    if assert_any_pattern(text, patterns, label):
        return
    snippet = text[-1200:]
    pytest.fail(
        f"Did not find expected {label}.\n"
        f"Tried patterns: {patterns}\n--- OUTPUT TAIL ---\n{snippet}\n--- END ---"
    )


def test_full_flow_basic(temp_workdir):
    repo_root = find_repo_root(Path(__file__).parent)

    cmds = [
        "Reset database",
        "Add a new user named Alice and id 1",
        "Create a new ticket titled Fix login and assign it to user Alice",
        "Create a new ticket titled Fix login and assign it to user Alice",
        "Create ticket titled Payment fails for user Bob",
        "View the title of ticket with id 1",
        "Show title for ticket id 9999",
        "Delete ticket 1",
    ]

    out = run_chat(cmds, repo_root=repo_root, workdir=temp_workdir)

    # Optional reset acknowledgement
    _ = assert_any_pattern(
        out,
        [r"database\s+reset", r"reset\s+successful", r"cleared\s+database"],
        "database reset acknowledgement (optional)"
    )

    # 1) Add user acknowledgement
    must_match_any(
        out,
        [
            r"user\s+is\s+added",
            r"added\s+user",
            r"created\s+user",
            r"user\s+id\s+already\s+exists",
            r"username\s+already\s+exists",
        ],
        "user-added acknowledgement"
    )

    # 2) Ticket creation acknowledgement with id
    must_match_any(
        out,
        [
            r"ticket\s+created.*id\s*\d+",
            r"created\s+ticket.*id\s*\d+",
            r"\bID\b\s*:\s*\d+",
        ],
        "ticket-created with id"
    )

    # 3) Duplicate ticket prevented
    must_match_any(
        out,
        [
            r"duplicate\s+title",
            r"duplicate\s+ticket",
            r"already\s+exists",
            r"title\s+already\s+exists",
        ],
        "duplicate-ticket prevention"
    )

    # 4) Non-existent user prevented
    must_match_any(
        out,
        [
            r"user\s+does\s+not\s+exist",
            r"unknown\s+user",
            r"no\s+such\s+user",
            r"cannot\s+create\s+ticket.*does\s+not\s+exist",
        ],
        "non-existent user prevention"
    )

    # 5) View ticket title by id (should contain Fix login)
    must_match_any(out, [r"\bfix\s+login\b"], "view-title happy path")

    # 6) Not-found ticket id graceful handling
    must_match_any(
        out,
        [
            r"\bticket\b.*not\s+found",
            r"no\s+such\s+ticket",
            r"does\s+not\s+exist",
            r"\bNo\s+ticket\b",
        ],
        "view-title not-found handling"
    )

    # 7) Delete ticket: accept either success (if implemented) OR unsupported message
    delete_supported = assert_any_pattern(
        out,
        [
            r"deleted\s+successfully",
            r"ticket\s+deleted",
            r"deleted\s+ticket",
        ],
        "delete ticket success"
    )
    if not delete_supported:
        must_match_any(
            out,
            [
                r"I\s+can'?t\s+help\s+with",
                r"cannot\s+help\s+with",
                r"unsupported\s+action",
                r"not\s+supported",
            ],
            "unsupported-action message"
        )
