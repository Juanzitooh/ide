import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from flask import current_app

FeedbackItem = Dict[str, str]


def _feedback_path() -> Path:
    feedback_file = current_app.config.get("FEEDBACK_FILE")
    return Path(feedback_file)


def _load_feedback() -> List[FeedbackItem]:
    path = _feedback_path()
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def _write_feedback(entries: List[FeedbackItem]) -> None:
    path = _feedback_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2, sort_keys=False)


def save_feedback(payload: FeedbackItem) -> FeedbackItem:
    entries = _load_feedback()
    next_id = len(entries) + 1
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    item = dict(payload)
    item["id"] = str(next_id)
    item["created_at"] = now
    entries.append(item)
    _write_feedback(entries)
    return item
