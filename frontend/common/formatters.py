from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
    return None


def format_datetime(value: Any) -> str:
    dt = parse_datetime(value)
    if not dt:
        return str(value) if value else "-"
    return dt.strftime("%d/%m/%Y %H:%M")


def format_relative_time(value: Any) -> str:
    from core.i18n import get_lang
    lang = get_lang()
    is_en = lang == "en"

    dt = parse_datetime(value)
    if not dt:
        return "-"
    
    # Ensure timezone naive comparison in local/system time
    if dt.tzinfo is not None:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now" if is_en else "vừa xong"
    if seconds < 3600:
        minutes = max(1, seconds // 60)
        return f"{minutes} min{'s' if minutes > 1 else ''} ago" if is_en else f"{minutes} phút trước"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago" if is_en else f"{hours} giờ trước"
    if seconds < 172800:
        return "Yesterday" if is_en else "Hôm qua"
    days = seconds // 86400
    if days < 30:
        return f"{days} days ago" if is_en else f"{days} ngày trước"
    return dt.strftime("%d/%m/%Y")


def truncate(value: Any, max_length: int = 80) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= max_length else f"{text[: max_length - 1]}…"
