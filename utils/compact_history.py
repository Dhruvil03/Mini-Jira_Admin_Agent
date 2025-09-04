from typing import List, Dict

def compact_history(history: List[Dict], max_window: int = 12, max_chars: int = 6000) -> List[Dict]:
    "Keep only the tail of the conversation within limits."
    if not history:
        return history
    # last max_window messages
    trimmed = history[-max_window:]
    # enforce char budget
    total = 0
    out = []
    for m in reversed(trimmed):
        c = len(m.get("content",""))
        if total + c > max_chars:
            break
        out.append(m)
        total += c
    return list(reversed(out))
