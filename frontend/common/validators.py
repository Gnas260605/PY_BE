from __future__ import annotations


def required(value: str | None, label: str) -> str | None:
    if value and value.strip():
        return None
    return f"{label} là bắt buộc"


def valid_email(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
        return "Email chưa đúng định dạng"
    return None


def min_length(value: str | None, length: int, label: str) -> str | None:
    if value and len(value.strip()) >= length:
        return None
    return f"{label} phải có tối thiểu {length} ký tự"
