"""
Midnight Garage: the tracker in your browser.

Run:  python dashboard.py
It opens http://127.0.0.1:5211 (only reachable from this computer).
"""

import json
import sys
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from knowledge import due_items, health_score, load_kb, watch_list
from mechanic import ai_status, ask_mechanic, diagnose_finish, diagnose_start
from tracker import load_log, save_log
from vin import decode_vin

HOST, PORT = "127.0.0.1", 5211
HERE = Path(__file__).parent
PAGE = HERE / "dashboard.html"
CAR_FILE = HERE / "car.json"   # your car profile, kept private like the log


# ---------- car profile ----------

def load_car():
    if not CAR_FILE.exists():
        return None
    with open(CAR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_car(car):
    with open(CAR_FILE, "w", encoding="utf-8") as f:
        json.dump(car, f, indent=2, ensure_ascii=False)


# ---------- helpers ----------

def to_km(value):
    """Accept 245000, '245 000' or '245,000'. Returns int or None."""
    text = str(value).replace(" ", "").replace(",", "")
    return int(text) if text.isdigit() else None


def bump_mileage(km):
    """Logging a service at a higher mileage moves the car's odometer forward."""
    car = load_car()
    if car and km > car.get("mileage", 0):
        car["mileage"] = km
        save_car(car)


# ---------- web server ----------

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return {}

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            body = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/state":
            log, car = load_log(), load_car()
            km = to_km(parse_qs(url.query).get("km", [""])[0])
            if km is None and car:
                km = car.get("mileage")
            kb = load_kb()
            due = due_items(log, km) if km is not None else None
            self.send_json({
                "car": car,
                "services": [it["service"] for it in kb["intervals"]],
                "history": sorted(({**e, "idx": i} for i, e in enumerate(log)),
                                  key=lambda e: e["km"], reverse=True),
                "due": due,
                "health": health_score(due),
                "watch": watch_list(log, km) if km is not None else None,
                "disclaimer": kb["disclaimer"],
                "ai": ai_status(),
            })
        elif url.path == "/api/vin":
            self.send_json(decode_vin(parse_qs(url.query).get("vin", [""])[0]))
        else:
            self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        data = self.read_json()

        if self.path == "/api/car":
            mileage = to_km(data.get("mileage", ""))
            model = str(data.get("model", "")).strip()
            if not model or mileage is None:
                return self.send_json({"error": "Model and a numeric mileage are required."}, 400)
            year = to_km(data.get("year", ""))
            car = {
                "nickname": str(data.get("nickname", "")).strip(),
                "make": str(data.get("make", "Mercedes-Benz")).strip(),
                "model": model,
                "engine": str(data.get("engine", "")).strip(),
                "body": str(data.get("body", "")).strip(),
                "year": year,
                "vin": str(data.get("vin", "")).strip().upper(),
                "mileage": mileage,
            }
            save_car(car)
            self.send_json({"car": car})

        elif self.path == "/api/mileage":
            km = to_km(data.get("mileage", ""))
            car = load_car()
            if not car or km is None:
                return self.send_json({"error": "Set up your car first, and use a numeric mileage."}, 400)
            car["mileage"] = km
            save_car(car)
            self.send_json({"car": car})

        elif self.path == "/api/job":
            # one job = one or more services done at the same time and mileage
            services = [str(s).strip().lower() for s in data.get("services", []) if str(s).strip()]
            km = to_km(data.get("km", ""))
            if not services or km is None:
                return self.send_json({"error": "Pick at least one service and enter the mileage."}, 400)
            when = str(data.get("date") or date.today())
            notes = str(data.get("notes", "")).strip()
            log = load_log()
            entries = [{"service": s, "km": km, "date": when, "notes": notes} for s in services]
            log.extend(entries)
            save_log(log)
            bump_mileage(km)
            self.send_json({"saved": entries})

        elif self.path == "/api/edit":
            log = load_log()
            idx = data.get("idx")
            if not isinstance(idx, int) or not 0 <= idx < len(log):
                return self.send_json({"error": "That entry doesn't exist anymore. Refresh the page."}, 404)
            entry = log[idx]
            if entry["service"] != data.get("orig_service") or entry["km"] != data.get("orig_km"):
                return self.send_json({"error": "The log changed. Refresh the page and try again."}, 409)
            service = str(data.get("service", "")).strip().lower()
            km = to_km(data.get("km", ""))
            if not service or km is None:
                return self.send_json({"error": "Service and a numeric mileage are required."}, 400)
            log[idx] = {"service": service, "km": km,
                        "date": str(data.get("date") or entry["date"]),
                        "notes": str(data.get("notes", "")).strip()}
            save_log(log)
            self.send_json({"updated": log[idx]})

        elif self.path == "/api/delete":
            log = load_log()
            idx = data.get("idx")
            # safety check: only delete if the entry at that position is the one the page showed
            if not isinstance(idx, int) or not 0 <= idx < len(log):
                return self.send_json({"error": "That entry doesn't exist anymore. Refresh the page."}, 404)
            entry = log[idx]
            if entry["service"] != data.get("service") or entry["km"] != data.get("km"):
                return self.send_json({"error": "The log changed. Refresh the page and try again."}, 409)
            log.pop(idx)
            save_log(log)
            self.send_json({"deleted": entry})

        elif self.path == "/api/ask":
            question = str(data.get("question", "")).strip()
            if not question:
                return self.send_json({"error": "Type a question first."}, 400)
            car = load_car()
            km = to_km(data.get("km", "")) or (car or {}).get("mileage")
            try:
                answer = ask_mechanic(question, load_log(), km)
            except RuntimeError as e:
                return self.send_json({"error": str(e)}, 503)
            self.send_json({"answer": answer})

        elif self.path == "/api/diagnose/start":
            symptom = str(data.get("symptom", "")).strip()
            if not symptom:
                return self.send_json({"error": "Describe the problem first."}, 400)
            try:
                questions = diagnose_start(symptom, load_log(), (load_car() or {}).get("mileage"))
            except RuntimeError as e:
                return self.send_json({"error": str(e)}, 503)
            self.send_json({"questions": questions})

        elif self.path == "/api/diagnose/finish":
            symptom = str(data.get("symptom", "")).strip()
            qa = [(str(p.get("q", "")), str(p.get("a", ""))) for p in data.get("qa", []) if isinstance(p, dict)]
            if not symptom:
                return self.send_json({"error": "Describe the problem first."}, 400)
            try:
                answer = diagnose_finish(symptom, qa, load_log(), (load_car() or {}).get("mileage"))
            except RuntimeError as e:
                return self.send_json({"error": str(e)}, 503)
            self.send_json({"answer": answer})

        else:
            self.send_json({"error": "not found"}, 404)

    def log_message(self, *args):
        pass  # keep the terminal quiet


if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    print(f"Midnight Garage running at {url}  (Ctrl+C to stop)")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDrive safe.")
