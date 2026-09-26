from __future__ import annotations

from pydantic import BaseModel


class LogAnalyticsArtifactResponse(BaseModel):
    key: str
    label: str
    path: str
    exists: bool
    size_bytes: int | None = None
    updated_at: str | None = None


class LogAnalyticsMetricResponse(BaseModel):
    metric: str
    value: int | str


class LogAnalyticsTopEventResponse(BaseModel):
    event: str
    count: int


class LogAnalyticsSecurityEventResponse(BaseModel):
    timestamp: str
    event: str
    username: str
    reason: str


class LogAnalyticsSummaryResponse(BaseModel):
    source_log: str
    generated: bool
    generated_at: str | None
    total_logs: int
    malformed: int | None
    unknown_event: int | None
    continuation_lines: int | None
    metrics: list[LogAnalyticsMetricResponse]
    top_events: list[LogAnalyticsTopEventResponse]
    security_events: list[LogAnalyticsSecurityEventResponse]
    report_excerpt: str
    artifacts: list[LogAnalyticsArtifactResponse]
