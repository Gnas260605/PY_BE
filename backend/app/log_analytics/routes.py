from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.core.auth import require_roles
from app.log_analytics.schemas import LogAnalyticsSummaryResponse
from app.log_analytics.service import (
    get_artifact_filename,
    get_artifact_path,
    get_log_analytics_summary,
)


router = APIRouter()


@router.get(
    "/log-analytics/summary",
    response_model=LogAnalyticsSummaryResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def log_analytics_summary_route() -> LogAnalyticsSummaryResponse:
    return get_log_analytics_summary()


@router.get(
    "/log-analytics/download/{artifact_key}",
    dependencies=[Depends(require_roles("ADMIN"))],
)
def download_log_analytics_artifact_route(artifact_key: str) -> FileResponse:
    path = get_artifact_path(artifact_key)
    return FileResponse(path, filename=get_artifact_filename(artifact_key))
