from fastapi import APIRouter

from app.health.service import get_health_status


router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return get_health_status()
