"""
W211 Maintenance Tracker - Step 2
Log services for my Mercedes E220 CDI, see the history, and check what's due.
"""

import json
from datetime import date
from pathlib import Path

# The log file lives next to this script, so it works from any folder.
LOG_FILE = Path(__file__).parent / "service_log.json"

# How often each service is due, in km.
# Starting values for an E220 CDI (OM646 engine) driven in Tunisia (heat, dust,
# variable diesel quality). Ask your mechanic and adjust these numbers.
INTERVALS = {
    "oil change": 10_000,
    "fuel filter": 30_000,
    "air filter": 30_000,
    "cabin filter": 20_000,
    "brake pads": 40_000,
    "gearbox oil": 60_000,
}

# How close (in km) counts as "due soon".
SOON_KM = 2_000


def load_log():
    """Read all saved services. Returns an empty list if there's no file yet."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(log):
    """Write every service back to the file."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def ask_mileage(prompt="Mileage (km): "):
    """Keep asking until we get a real number (accepts 245000, 245 000 or 245,000)."""
    while True:
        text = input(prompt).replace(" ", "").replace(",", "")
        if text.isdigit():
            return int(text)
        print("  Numbers only, like 245000. Try again.")


def pick_service():
    """Show the known services as a numbered list, or let the user type their own."""
    names = list(INTERVALS)
    for i, name in enumerate(names, start=1):
        print(f"  {i}) {name}")
    print("  ...or type anything else (e.g. new suspension)")
    while True:
        text = input("What was done: ").strip()
        if text.isdigit() and 1 <= int(text) <= len(names):
            return names[int(text) - 1]
        if text:
            return text.lower()


def add_service(log):
    print("\n--- Add a service ---")
    service = pick_service()
    km = ask_mileage()
    today = str(date.today())
    when = input(f"Date (Enter = today, {today}): ").strip() or today
    notes = input("Notes (parts, garage, price... optional): ").strip()

    log.append({"service": service, "km": km, "date": when, "notes": notes})
    save_log(log)
    print(f"  Saved: {service} at {km:,} km")


def show_history(log):
    print("\n--- Service history ---")
    if not log:
        print("  Nothing logged yet.")
        return
    # Newest (highest mileage) first
    for entry in sorted(log, key=lambda e: e["km"], reverse=True):
        line = f"  {entry['date']}  {entry['km']:>9,} km  {entry['service']}"
        if entry["notes"]:
            line += f"  ({entry['notes']})"
        print(line)


def last_done_km(log, service):
    """The highest mileage this service was logged at, or None if never."""
    kms = [e["km"] for e in log if e["service"].lower() == service]
    return max(kms) if kms else None


def compute_status(last_km, interval, current_km):
    """The logic from my spec, shared by the terminal app and the dashboard.
    Returns (state, next_due, km_left) where state is overdue / due_now / soon / ok."""
    next_due = last_km + interval          # Step 1
    km_left = next_due - current_km        # Step 2
    if km_left < 0:
        return "overdue", next_due, km_left
    if km_left == 0:
        return "due_now", next_due, km_left
    if km_left <= SOON_KM:
        return "soon", next_due, km_left
    return "ok", next_due, km_left


def status_for(service, last_km, interval, current_km):
    """
    Spec written by midnightblue:
      Step 1: next due = last done + interval
      Step 2: km left  = next due - current mileage
      If km left is negative        -> OVERDUE by that many km
      If km left is exactly 0       -> DUE NOW: reached, change it now
      Else if km left is 1 to 2,000 -> SOON, in that many km
      Otherwise                     -> OK, next one at the next-due mileage
    """
    state, next_due, km_left = compute_status(last_km, interval, current_km)

    if state == "overdue":
        return f"  OVERDUE  {service:<15} by {abs(km_left):,} km"
    elif state == "due_now":
        return f"  DUE NOW  {service:<15} reached, change it now"
    elif state == "soon":
        return f"  SOON     {service:<15} in {km_left:,} km"
    else:
        return f"  OK       {service:<15} next at {next_due:,} km"


def check_due(log):
    print("\n--- What's due ---")
    current_km = ask_mileage("Current mileage (km): ")
    for service, interval in INTERVALS.items():
        last_km = last_done_km(log, service)
        if last_km is None:
            print(f"  ?        {service:<15} never logged")
        else:
            print(status_for(service, last_km, interval, current_km))


def main():
    log = load_log()
    print("=== W211 E220 CDI Maintenance Tracker ===")
    while True:
        print("\n1) Add a service")
        print("2) Show history")
        print("3) What's due?")
        print("4) Quit")
        choice = input("> ").strip()
        if choice == "1":
            add_service(log)
        elif choice == "2":
            show_history(log)
        elif choice == "3":
            check_due(log)
        elif choice == "4":
            print("Drive safe.")
            break
        else:
            print("  Pick 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
