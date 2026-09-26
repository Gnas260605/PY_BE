from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from app.core.errors import NotFoundError
from app.log_analytics.schemas import (
    LogAnalyticsArtifactResponse,
    LogAnalyticsMetricResponse,
    LogAnalyticsSecurityEventResponse,
    LogAnalyticsSummaryResponse,
    LogAnalyticsTopEventResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PERL_DIR = PROJECT_ROOT / "perl"
OUTPUT_DIR = PERL_DIR / "output"
REPORTS_DIR = PERL_DIR / "reports"
SAMPLE_LOG = PERL_DIR / "samples" / "backend_sample.log"

ARTIFACTS: dict[str, tuple[str, Path]] = {
    "logs_csv": ("Parsed logs CSV", OUTPUT_DIR / "logs.csv"),
    "parser_stats": ("Parser stats JSON", OUTPUT_DIR / "logs_stats.json"),
    "summary_csv": ("Summary CSV", REPORTS_DIR / "summary.csv"),
    "security_csv": ("Security events CSV", REPORTS_DIR / "security_events.csv"),
    "report_txt": ("Text report", REPORTS_DIR / "report.txt"),
}


def get_artifact_path(key: str) -> Path:
    artifact = ARTIFACTS.get(key)
    if artifact is None:
        raise NotFoundError("LOG_ANALYTICS_ARTIFACT_NOT_FOUND")

    path = artifact[1].resolve()
    allowed_roots = (OUTPUT_DIR.resolve(), REPORTS_DIR.resolve())
    if not any(path == root or root in path.parents for root in allowed_roots):
        raise NotFoundError("LOG_ANALYTICS_ARTIFACT_NOT_FOUND")
    if not path.is_file():
        raise NotFoundError("LOG_ANALYTICS_ARTIFACT_NOT_FOUND")
    return path


def get_artifact_filename(key: str) -> str:
    return get_artifact_path(key).name


def get_log_analytics_summary() -> LogAnalyticsSummaryResponse:
    artifacts = [_artifact_response(key, label, path) for key, (label, path) in ARTIFACTS.items()]
    summary_metrics = _read_summary_metrics(ARTIFACTS["summary_csv"][1])
    security_events = _read_security_events(ARTIFACTS["security_csv"][1])
    parser_stats = _read_parser_stats(ARTIFACTS["parser_stats"][1])
    logs_rows = _read_log_rows(ARTIFACTS["logs_csv"][1])

    top_events = _top_events_from_logs(logs_rows)
    if not top_events:
        top_events = _top_events_from_summary(summary_metrics)

    total_logs = _metric_as_int(summary_metrics, "total_logs")
    if total_logs == 0 and parser_stats:
        total_logs = int(parser_stats.get("parsed") or 0)
    if total_logs == 0 and logs_rows:
        total_logs = len(logs_rows)

    generated_at = _latest_updated_at([artifact for artifact in artifacts if artifact.exists])
    generated = any(artifact.exists for artifact in artifacts)
    source_log = str(SAMPLE_LOG.relative_to(PROJECT_ROOT)) if SAMPLE_LOG.exists() else "not available"

    return LogAnalyticsSummaryResponse(
        source_log=source_log,
        generated=generated,
        generated_at=generated_at,
        total_logs=total_logs,
        malformed=_optional_int(parser_stats, "malformed"),
        unknown_event=_optional_int(parser_stats, "unknown_event"),
        continuation_lines=_optional_int(parser_stats, "continuation_lines"),
        metrics=[
            LogAnalyticsMetricResponse(metric=metric, value=value)
            for metric, value in summary_metrics.items()
        ],
        top_events=top_events,
        security_events=security_events,
        report_excerpt=_read_excerpt(ARTIFACTS["report_txt"][1]),
        artifacts=artifacts,
    )


def _artifact_response(key: str, label: str, path: Path) -> LogAnalyticsArtifactResponse:
    exists = path.is_file()
    stat = path.stat() if exists else None
    updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds") if stat else None
    return LogAnalyticsArtifactResponse(
        key=key,
        label=label,
        path=str(path.relative_to(PROJECT_ROOT)),
        exists=exists,
        size_bytes=stat.st_size if stat else None,
        updated_at=updated_at,
    )


def _read_summary_metrics(path: Path) -> dict[str, int | str]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        values: dict[str, int | str] = {}
        for row in reader:
            metric = (row.get("metric") or "").strip()
            raw_value = (row.get("value") or "").strip()
            if not metric:
                continue
            values[metric] = int(raw_value) if raw_value.isdigit() else raw_value
        return values


def _read_security_events(path: Path) -> list[LogAnalyticsSecurityEventResponse]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return [
            LogAnalyticsSecurityEventResponse(
                timestamp=row.get("timestamp") or "",
                event=row.get("event") or "",
                username=row.get("username") or "",
                reason=row.get("reason") or "",
            )
            for row in reader
        ]


def _read_parser_stats(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        key: int(value)
        for key, value in payload.items()
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    }


def _read_log_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _top_events_from_logs(rows: list[dict[str, str]]) -> list[LogAnalyticsTopEventResponse]:
    counter = Counter(row.get("event") for row in rows if row.get("event"))
    return [
        LogAnalyticsTopEventResponse(event=event, count=count)
        for event, count in counter.most_common(8)
    ]


def _top_events_from_summary(metrics: dict[str, int | str]) -> list[LogAnalyticsTopEventResponse]:
    mapping = {
        "login_success": "LOGIN_SUCCESS",
        "login_failed": "LOGIN_FAILED",
        "ticket_created": "TICKET_CREATED",
        "ticket_closed": "TICKET_CLOSED",
        "warning": "WARNING",
        "error": "ERROR",
    }
    events = [
        LogAnalyticsTopEventResponse(event=event, count=int(metrics.get(metric) or 0))
        for metric, event in mapping.items()
        if int(metrics.get(metric) or 0) > 0
    ]
    return sorted(events, key=lambda item: item.count, reverse=True)


def _read_excerpt(path: Path, *, max_chars: int = 2500) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n..."


def _metric_as_int(metrics: dict[str, int | str], key: str) -> int:
    value = metrics.get(key)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


def _optional_int(values: dict[str, int], key: str) -> int | None:
    return int(values[key]) if key in values else None


def _latest_updated_at(artifacts: list[LogAnalyticsArtifactResponse]) -> str | None:
    updated = [artifact.updated_at for artifact in artifacts if artifact.updated_at]
    return max(updated) if updated else None
