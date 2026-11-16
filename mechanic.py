"""
The AI mechanic's brain.

It lives in one place on purpose: today it uses a free local model through Ollama,
and later it can switch to Claude by changing only this file.

Rule we learned: CODE calculates, the MODEL explains.
So the code works out mileages, due dates and safety warnings, and the model only talks.
"""

import json
import re
import urllib.error
import urllib.request

from knowledge import due_items, kb_context

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "llama3.2:3b"

SYSTEM_PROMPT = (
    "You are a friendly, practical mechanic who knows the Mercedes W211 E220 CDI well "
    "(OM646 2.2 diesel). The owner drives in Tunisia: heat, dust, and diesel quality that varies. "
    "Use the owner's service history and the model knowledge below. Do not invent mileages: "
    "the numbers given to you are already calculated and correct. "
    "Keep it short and practical. If you are not sure, say so."
)

SAFETY_WORDS = ("brake", "frein", "steer", "direction", "tyre", "tire", "pneu", "sbc", "wheel", "roue")
SAFETY_NOTE = "\n\n⚠️ This involves safety (brakes, steering or tyres). Have a mechanic check it before driving far."

FALLBACK_QUESTIONS = [
    "When does it happen: cold engine, warm engine, or all the time?",
    "Does it happen while driving, braking, turning, or standing still?",
    "Is there a sound, a smell, smoke, or a warning light? Describe it.",
    "When did it start, and has anything been repaired recently?",
]


def history_context(log, current_km=None):
    """Turn the service log into plain text the model can read. The code does the math."""
    lines = ["SERVICE HISTORY (newest first):"]
    if not log:
        lines.append("- nothing logged yet")
    for e in sorted(log, key=lambda e: e["km"], reverse=True):
        note = f" ({e['notes']})" if e.get("notes") else ""
        ago = f", {current_km - e['km']:,} km ago" if current_km else ""
        lines.append(f"- {e['date']}: {e['service']} at {e['km']:,} km{ago}{note}")

    if current_km is not None:
        lines.append(f"\nCURRENT MILEAGE: {current_km:,} km")
        lines.append("MAINTENANCE STATUS (already calculated):")
        for r in due_items(log, current_km):
            if r["state"] == "never":
                lines.append(f"- {r['service']}: never logged")
            else:
                lines.append(f"- {r['service']}: {r['state'].replace('_', ' ').upper()} "
                             f"(last at {r['last_km']:,} km, recommended every {r['interval']:,} km)")
        lines.append("\n" + kb_context(log, current_km))
    return "\n".join(lines)


def ai_status():
    """Is Ollama running, and is our model downloaded?"""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1) as r:
            models = [m["name"] for m in json.load(r).get("models", [])]
    except (urllib.error.URLError, OSError, ValueError):
        return {"online": False, "model_ready": False, "model": MODEL}
    return {"online": True, "model_ready": any(m.startswith(MODEL) for m in models), "model": MODEL}


def _chat(system, user):
    """Send one request to the local model and return its text."""
    payload = {"model": MODEL, "stream": False,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)["message"]["content"].strip()
    except urllib.error.URLError as e:
        raise RuntimeError("The local AI isn't running. Start Ollama and try again.") from e


def _with_safety(text, *topics):
    """The code, not the model, decides when to add the safety warning."""
    joined = " ".join(topics).lower()
    return text + SAFETY_NOTE if any(w in joined for w in SAFETY_WORDS) else text


# ---------- mode 1: quick question ----------

def ask_mechanic(question, log, current_km=None):
    answer = _chat(SYSTEM_PROMPT + "\n\n" + history_context(log, current_km), question)
    return _with_safety(answer, question, answer)


# ---------- mode 2: diagnosis session ----------

def diagnose_start(symptom, log, current_km=None):
    """Step 1: the mechanic asks the owner a few questions before guessing."""
    prompt = (
        f"The owner reports: \"{symptom}\".\n"
        "Before diagnosing, ask exactly 4 short questions a good mechanic would ask to narrow it down "
        "(when it happens, conditions, sounds/smells/lights, recent work). "
        "Return ONLY the 4 questions, one per line, no numbering, no intro."
    )
    raw = _chat(SYSTEM_PROMPT + "\n\n" + history_context(log, current_km), prompt)
    questions = []
    for line in raw.splitlines():
        q = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()
        if q.endswith("?") and len(q) > 8:
            questions.append(q)
    # small models don't always follow the format, so the code has a safe fallback
    return questions[:4] if len(questions) >= 2 else FALLBACK_QUESTIONS


def diagnose_finish(symptom, qa, log, current_km=None):
    """Step 2: with the answers, give a ranked list of likely causes."""
    answers = "\n".join(f"Q: {q}\nA: {a or '(no answer)'}" for q, a in qa)
    prompt = (
        f"The owner reports: \"{symptom}\".\nTheir answers:\n{answers}\n\n"
        "Give a diagnosis in this format:\n"
        "Most likely causes (ranked, with a one-line reason each, max 3)\n"
        "What to check first\n"
        "How urgent it is (drive normally / book soon / stop driving)\n"
        "Use the service history and known issues. Keep it under 180 words."
    )
    answer = _chat(SYSTEM_PROMPT + "\n\n" + history_context(log, current_km), prompt)
    return _with_safety(answer, symptom, answers, answer)
