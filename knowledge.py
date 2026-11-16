"""
The model knowledge base: service intervals and known issues for a specific car.
v1 has one car: the W211 E 220 CDI (OM646). Adding a car = adding a JSON file.
"""

import json
from datetime import date
from pathlib import Path

KB_FILE = Path(__file__).parent / "knowledge" / "w211_om646.json"
SOON_KM = 2_000
SOON_DAYS = 30
SEVERITY_ORDER = {"safety": 0, "important": 1, "watch": 2}


def load_kb():
    with open(KB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _last_entry(log, service):
    """Most recent entry (highest mileage) for a service, or None."""
    entries = [e for e in log if e["service"].lower() == service]
    return max(entries, key=lambda e: e["km"]) if entries else None


def _days_since(iso_date, today):
    try:
        return (today - date.fromisoformat(iso_date)).days
    except (TypeError, ValueError):
        return None


def due_items(log, current_km, today=None):
    """
    For every interval: whichever comes first, mileage or time.
    Returns a list of dicts with state overdue / due_now / soon / ok / never.
    """
    today = today or date.today()
    rows = []
    for it in load_kb()["intervals"]:
        service = it["service"]
        last = _last_entry(log, service)
        row = {"service": service, "interval": it["every_km"], "months": it.get("every_months"), "why": it["why"]}
        if last is None:
            rows.append({**row, "state": "never"})
            continue

        # mileage side (my original spec)
        next_km = last["km"] + it["every_km"]
        km_left = next_km - current_km
        # time side
        days_left = None
        if it.get("every_months"):
            since = _days_since(last["date"], today)
            if since is not None:
                days_left = it["every_months"] * 30 - since

        if km_left < 0 or (days_left is not None and days_left < 0):
            state = "overdue"
        elif km_left == 0 or days_left == 0:
            state = "due_now"
        elif km_left <= SOON_KM or (days_left is not None and days_left <= SOON_DAYS):
            state = "soon"
        else:
            state = "ok"
        rows.append({**row, "state": state, "last_km": last["km"], "next_due": next_km,
                     "km_left": km_left, "days_left": days_left})
    return rows


def watch_list(log, current_km):
    """Known issues that matter at this mileage, minus the ones you've already dealt with."""
    done = {e["service"].lower() for e in log}
    items = [i for i in load_kb()["issues"]
             if current_km >= i["relevant_from_km"] and not done & set(i.get("related_services", []))]
    return sorted(items, key=lambda i: (SEVERITY_ORDER.get(i["severity"], 9), -i["relevant_from_km"]))


def kb_context(log, current_km):
    """Plain-text knowledge for the AI mechanic: intervals status + issues to watch."""
    kb = load_kb()
    lines = [f"MODEL KNOWLEDGE ({kb['car']}):", "Known issues relevant at this mileage:"]
    for i in watch_list(log, current_km) if current_km else kb["issues"]:
        lines.append(f"- [{i['severity']}] {i['name']}: symptoms: {'; '.join(i['symptoms'])}. Check: {i['check']}")
    return "\n".join(lines)
