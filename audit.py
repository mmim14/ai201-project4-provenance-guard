"""Audit log: append-only record of every classification, stored as a JSON array.

Each /submit call writes one structured entry (timestamp, submission_id,
creator_id, signal scores, combined confidence, label, status) to a JSON file.
Kept as a single JSON array (rather than JSON-lines) so the later appeals
workflow can look up and update a record by its submission_id.
"""

import json
import os
import threading

LOG_PATH = os.path.join(os.path.dirname(__file__), "audit_log.json")

# Serialize read-modify-write so concurrent requests don't clobber the file.
_lock = threading.Lock()


def _read_all() -> list:
    """Return all entries, or an empty list if the log is missing/unreadable."""
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_all(entries: list) -> None:
    with open(LOG_PATH, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)


def append_entry(entry: dict) -> None:
    """Append one entry to the audit log."""
    with _lock:
        entries = _read_all()
        entries.append(entry)
        _write_all(entries)


def read_recent(limit: int = 20) -> list:
    """Return the most recent entries, newest first."""
    with _lock:
        entries = _read_all()
    return entries[-limit:][::-1]


def add_appeal(submission_id: str, appeal: dict) -> dict | None:
    """Attach an appeal to a record and mark it "under review".

    Returns the updated entry, or None if no record matches submission_id.
    """
    with _lock:
        entries = _read_all()
        for entry in entries:
            if entry.get("submission_id") == submission_id:
                entry["status"] = "under review"
                entry.setdefault("appeals", []).append(appeal)
                _write_all(entries)
                return entry
        return None
