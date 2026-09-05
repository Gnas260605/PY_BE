from __future__ import annotations

from datetime import datetime
from typing import Any


def format_datetime(value: Any) -> str:
    if not value:
        return "-"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    return str(value)


def truncate(value: Any, max_length: int = 80) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= max_length else f"{text[: max_length - 1]}…"
