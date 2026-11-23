"""
The car journal (v1.2): photos, notes and moods from the car's life.

Everything stays on this PC for now: entries in journal.json, photos in journal_photos/.
Each entry is marked public or private (public by default), so it's ready for the
online version later. Nothing is shared until then.
"""

import base64
import json
import re
import uuid
from pathlib import Path

HERE = Path(__file__).parent
JOURNAL_FILE = HERE / "journal.json"
PHOTO_DIR = HERE / "journal_photos"
MAX_PHOTOS = 12
MAX_PHOTO_BYTES = 4 * 1024 * 1024          # the page shrinks photos first, so this is generous
PHOTO_NAME = re.compile(r"^[0-9a-f]{32}\.jpg$")   # only names we created ourselves


def load_journal():
    if not JOURNAL_FILE.exists():
        return []
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_journal(entries):
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def save_photo(data_url):
    """
    Store one photo sent by the page as a JPEG data URL. Returns the file name.
    The page redraws every photo on a canvas before sending it, which also drops
    hidden data like GPS location.
    """
    prefix = "data:image/jpeg;base64,"
    if not isinstance(data_url, str) or not data_url.startswith(prefix):
        raise ValueError("Photos must be JPEG images.")
    raw = base64.b64decode(data_url[len(prefix):], validate=True)
    if len(raw) > MAX_PHOTO_BYTES or not raw.startswith(b"\xff\xd8"):
        raise ValueError("That photo is too big or not a real JPEG.")
    PHOTO_DIR.mkdir(exist_ok=True)
    name = uuid.uuid4().hex + ".jpg"
    (PHOTO_DIR / name).write_bytes(raw)
    return name


def photo_path(name):
    """Path of a stored photo, or None if the name isn't one of ours (blocks ../ tricks)."""
    if not PHOTO_NAME.match(name or ""):
        return None
    p = PHOTO_DIR / name
    return p if p.exists() else None


def delete_photos(names):
    for n in names:
        p = photo_path(n)
        if p:
            p.unlink()


def journal_context(entries, limit=8):
    """Plain text for the AI mechanic: the latest journal entries (notes only, it can't see photos yet)."""
    if not entries:
        return ""
    lines = ["OWNER'S CAR JOURNAL (newest first, the owner's own words):"]
    for e in sorted(entries, key=lambda e: e["date"], reverse=True)[:limit]:
        bits = [e["date"]]
        if e.get("km"):
            bits.append(f"{e['km']:,} km")
        if e.get("job"):
            bits.append(f"job: {e['job']}")
        if e.get("mood"):
            bits.append(f"mood: {e['mood']}")
        note = f": {e['note']}" if e.get("note") else ""
        lines.append(f"- {e['title']} ({', '.join(bits)}){note}")
    lines.append("If something in the journal relates to the owner's question, mention it naturally.")
    return "\n".join(lines)
