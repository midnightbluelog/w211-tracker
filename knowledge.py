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


CHECK_TRUST_DAYS = 90   # v1.1 decision 2: a "looks fine" check is trusted for 3 months
CHECK_CREDIT = 0.5      # v1.1 decision 1: a check counts half, because nothing was serviced


def _last_check(checks, service, today):
    """Most recent check for a service that's still trusted (younger than CHECK_TRUST_DAYS), or None."""
    fresh = [c for c in (checks or []) if c["service"] == service
             and (_days_since(c["date"], today) or 0) <= CHECK_TRUST_DAYS]
    return max(fresh, key=lambda c: c["date"]) if fresh else None


def due_items(log, current_km, today=None, checks=None):
    """
    For every interval: whichever comes first, mileage or time.
    Returns a list of dicts with state overdue / due_now / soon / ok / never,
    or checked_ok / checked_bad when there's no service on record but the owner checked it (v1.1).
    """
    today = today or date.today()
    rows = []
    for it in load_kb()["intervals"]:
        service = it["service"]
        last = _last_entry(log, service)
        row = {"service": service, "interval": it["every_km"], "months": it.get("every_months"),
               "why": it["why"], "check": it.get("check")}
        if last is None:
            chk = _last_check(checks, service, today)
            if chk is None:
                rows.append({**row, "state": "never"})
            else:
                # decision 3: "looks bad" is treated like overdue
                state = "checked_ok" if chk["result"] == "fine" else "checked_bad"
                rows.append({**row, "state": state, "checked_on": chk["date"],
                             "check_days_left": CHECK_TRUST_DAYS - (_days_since(chk["date"], today) or 0)})
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


SAFETY_SERVICES = {"brake pads", "brake fluid"}
SAFETY_CAP = 60   # overdue brakes: health can't go above this


def _item_score(row):
    """
    How healthy one service is, from 0 to 1, based on how much of its interval is left
    (by km or time, whichever is worse).
      more than 20% left  -> 1.0  (normal wear isn't punished)
      20% -> 0% left      -> 1.0 slides to 0.6
      overdue             -> 0.6 slides to 0 (0 once it's 50% over)
    """
    life = row["km_left"] / row["interval"]
    if row.get("days_left") is not None and row.get("months"):
        life = min(life, row["days_left"] / (row["months"] * 30))
    if life >= 0.2:
        return 1.0
    if life >= 0:
        return 0.6 + 0.4 * (life / 0.2)
    return max(0.0, 0.6 + 0.6 * (life / 0.5))


def health_score(rows):
    """
    Two numbers, both weighted by how important each service is:
      info      = how much of the car we have data on
      condition = how healthy the services we DO know about are
      health    = condition x info  (unknown services pull health down until you log them)
    Overdue brakes cap health at SAFETY_CAP.
    """
    if not rows:
        return None
    weights = {it["service"]: it.get("weight", 1) for it in load_kb()["intervals"]}

    def known_weight(r):
        # a "looks fine" check only counts half: someone looked, but nothing was serviced
        w = weights.get(r["service"], 1)
        return w * CHECK_CREDIT if r["state"] == "checked_ok" else w

    def score(r):
        if r["state"] == "checked_ok":
            return 1.0
        if r["state"] == "checked_bad":
            return 0.0
        return _item_score(r)

    total = sum(weights.get(r["service"], 1) for r in rows)
    known = [r for r in rows if r["state"] != "never"]
    known_w = sum(known_weight(r) for r in known)
    info = known_w / total
    condition = (sum(known_weight(r) * score(r) for r in known) / known_w) if known else 0
    health = round(100 * condition * info)
    capped = any(r["service"] in SAFETY_SERVICES and r["state"] in ("overdue", "checked_bad") for r in known)
    if capped:
        health = min(health, SAFETY_CAP)
    return {
        "health": health,
        "info": round(100 * info),
        "condition": round(100 * condition),
        "unknown": [r["service"] for r in rows if r["state"] == "never"],
        "brakes_capped": capped,
    }


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
