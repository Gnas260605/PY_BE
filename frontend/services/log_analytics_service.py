from __future__ import annotations

from typing import Any

from core.http_client import http_client


class LogAnalyticsService:
    async def get_summary(self) -> dict[str, Any]:
        return await http_client.get("/log-analytics/summary")

    async def download_artifact(self, artifact_key: str) -> bytes:
        return await http_client.download_file(f"/log-analytics/download/{artifact_key}")


log_analytics_service = LogAnalyticsService()
