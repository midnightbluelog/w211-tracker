"""
The AI mechanic's brain.

It lives in one place on purpose: today it uses a free local model through Ollama,
and later it can switch to Claude by changing only this file.
"""

import json
import urllib.error
import urllib.request

from tracker import INTERVALS, compute_status, last_done_km

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "llama3.2:3b"

SYSTEM_PROMPT = (
    "You are a friendly, practical mechanic who knows the Mercedes W211 E220 CDI well "
    "(2004, OM646 2.2 diesel engine, manual gearbox). The owner drives in Tunisia: heat, dust, "
    "and diesel quality that varies. Use the owner's service history below when you answer. "
    "Keep it short and practical: the most likely causes first, what to check, and when to see a mechanic. "
    "If something affects safety (brakes, steering, tyres), say so clearly. If you are not sure, say that too."
)


def history_context(log, current_km=None):
    """Turn the service log into plain text the model can read."""
    lines = ["SERVICE HISTORY (newest first):"]
    if not log:
        lines.append("- nothing logged yet")
    for e in sorted(log, key=lambda e: e["km"], reverse=True):
        note = f" ({e['notes']})" if e.get("notes") else ""
        lines.append(f"- {e['date']}: {e['service']} at {e['km']:,} km{note}")

    if current_km is not None:
        lines.append(f"\nCURRENT MILEAGE: {current_km:,} km")
        lines.append("MAINTENANCE STATUS:")
        for service, interval in INTERVALS.items():
            last = last_done_km(log, service)
            if last is None:
                lines.append(f"- {service}: never logged")
                continue
            state, next_due, km_left = compute_status(last, interval, current_km)
            ago = current_km - last
            lines.append(
                f"- {service}: last done {ago:,} km ago (at {last:,} km). "
                f"Recommended every {interval:,} km. Status: {state.replace('_', ' ').upper()}."
            )
    return "\n".join(lines)


def ai_status():
    """Is Ollama running, and is our model downloaded?"""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1) as r:
            models = [m["name"] for m in json.load(r).get("models", [])]
    except (urllib.error.URLError, OSError, ValueError):
        return {"online": False, "model_ready": False, "model": MODEL}
    return {"online": True, "model_ready": any(m.startswith(MODEL) for m in models), "model": MODEL}


def ask_mechanic(question, log, current_km=None):
    """Ask the local model a question, with the car's history as context."""
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + history_context(log, current_km)},
            {"role": "user", "content": question},
        ],
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)["message"]["content"].strip()
    except urllib.error.URLError as e:
        raise RuntimeError("The local AI isn't running. Start Ollama and try again.") from e
