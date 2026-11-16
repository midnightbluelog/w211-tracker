"""
W211 dashboard: the tracker in your browser.

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

from mechanic import ai_status, ask_mechanic
from tracker import INTERVALS, compute_status, last_done_km, load_log, save_log

HOST, PORT = "127.0.0.1", 5211
PAGE = Path(__file__).parent / "dashboard.html"


def to_km(value):
    """Accept 245000, '245 000' or '245,000'. Returns int or None."""
    text = str(value).replace(" ", "").replace(",", "")
    return int(text) if text.isdigit() else None


def due_list(log, current_km):
    rows = []
    for service, interval in INTERVALS.items():
        last = last_done_km(log, service)
        if last is None:
            rows.append({"service": service, "state": "never", "interval": interval})
            continue
        state, next_due, km_left = compute_status(last, interval, current_km)
        rows.append({"service": service, "state": state, "km_left": km_left,
                     "next_due": next_due, "last_km": last, "interval": interval})
    return rows


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
            log = load_log()
            km = to_km(parse_qs(url.query).get("km", [""])[0])
            self.send_json({
                "services": list(INTERVALS),
                # each entry carries its position in the file, so the page can ask to delete it
                "history": sorted(({**e, "idx": i} for i, e in enumerate(log)),
                                  key=lambda e: e["km"], reverse=True),
                "due": due_list(log, km) if km is not None else None,
                "ai": ai_status(),
            })
        else:
            self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        data = self.read_json()
        if self.path == "/api/service":
            service = str(data.get("service", "")).strip().lower()
            km = to_km(data.get("km", ""))
            if not service or km is None:
                return self.send_json({"error": "Service and a numeric mileage are required."}, 400)
            entry = {"service": service, "km": km,
                     "date": str(data.get("date") or date.today()),
                     "notes": str(data.get("notes", "")).strip()}
            log = load_log()
            log.append(entry)
            save_log(log)
            self.send_json({"saved": entry})
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
            try:
                answer = ask_mechanic(question, load_log(), to_km(data.get("km", "")))
            except RuntimeError as e:
                return self.send_json({"error": str(e)}, 503)
            self.send_json({"answer": answer})
        else:
            self.send_json({"error": "not found"}, 404)

    def log_message(self, *args):
        pass  # keep the terminal quiet


if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    print(f"W211 dashboard running at {url}  (Ctrl+C to stop)")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDrive safe.")
